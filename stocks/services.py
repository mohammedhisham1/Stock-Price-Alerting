import requests
import logging
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.db import transaction
import pytz
from .models import Stock, StockPrice

logger = logging.getLogger(__name__)


class StockDataService:
    "Service for fetching stock data with rate limiting"
    
    def __init__(self):
        self.api_key = settings.TWELVE_DATA_API_KEY
        self.base_url = "https://api.twelvedata.com"

    def is_market_open(self):
        eastern = pytz.timezone('US/Eastern')
        et_now = timezone.now().astimezone(eastern)

        if et_now.weekday() >= 5:  # Sat=5, Sun=6
            return False

        market_open = et_now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = et_now.replace(hour=16, minute=0, microsecond=0)
        return market_open <= et_now <= market_close

    def to_decimal(self, value):
        return Decimal(str(value)) if value else None

    def fetch_and_update_stock(self, symbol):
        try:
            if not self.is_market_open():
                logger.info(f"Market closed, skipping {symbol}")
                return

            logger.info(f"Fetching {symbol}")

            response = requests.get(
                f"{self.base_url}/quote",
                params={'symbol': symbol, 'apikey': self.api_key},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if data.get('code') == 429:
                logger.error(f"Rate limit exceeded for {symbol}")
                return

            if 'close' not in data:
                logger.error(f"Invalid response for {symbol}: {data}")
                return

            quote_data = {
                'price': self.to_decimal(data.get('close')),
                'open': self.to_decimal(data.get('open')),
                'high': self.to_decimal(data.get('high')),
                'low': self.to_decimal(data.get('low')),
                'volume': int(data['volume']) if data.get('volume') else None,
            }

            stock = Stock.objects.get(symbol=symbol)
            now = timezone.now()

            with transaction.atomic():
                StockPrice.objects.create(
                    stock=stock,
                    price=quote_data['price'],
                    open_price=quote_data.get('open'),
                    high_price=quote_data.get('high'),
                    close_price=quote_data['price'],
                    low_price=quote_data.get('low'),
                    volume=quote_data.get('volume'),
                    timestamp=now
                )

                stock.current_price = quote_data['price']
                stock.last_updated = now
                stock.save(update_fields=["current_price", "last_updated"])

            logger.info(f"Updated {symbol}: ${quote_data['price']}")
            return True

        except Stock.DoesNotExist:
            logger.error(f"Stock {symbol} not found")
        except requests.RequestException as e:
            logger.error(f"API request failed for {symbol}: {e}")
        except Exception as e:
            logger.error(f"Failed to update {symbol}: {e}")



