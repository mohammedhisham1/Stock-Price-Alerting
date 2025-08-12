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
        """Check if US stock market is currently open"""
        eastern = pytz.timezone('US/Eastern')
        et_now = timezone.now().astimezone(eastern)
        
        # Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday
        if et_now.weekday() >= 5:  # Saturday=5, Sunday=6
            return False
            
        market_open = et_now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = et_now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_open <= et_now <= market_close
        
    def fetch_and_update_stock(self, symbol):
        """Fetch quote and update stock price in database"""
        try:
            # Skip API call if market is closed (unless forced)
            if not self.is_market_open():
                logger.info(f"Market is closed, skipping update for {symbol}")
                return None
                
            logger.info(f"Fetching and updating {symbol}")
            
            # Fetch quote data
            response = requests.get(
                f"{self.base_url}/quote",
                params={'symbol': symbol, 'apikey': self.api_key},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Handle rate limit or invalid response
            if data.get('code') == 429:
                logger.error(f"Rate limit exceeded for {symbol}")
                return None
                
            if 'close' not in data:
                logger.error(f"Invalid response for {symbol}: {data}")
                return None
            
            # Parse quote data
            def to_decimal(value):
                return Decimal(str(value)) if value else None
                
            quote_data = {
                'price': to_decimal(data.get('close', 0)),
                'open': to_decimal(data.get('open')),
                'high': to_decimal(data.get('high')),
                'low': to_decimal(data.get('low')),
                'volume': int(data['volume']) if data.get('volume') else None,
            }
            
            # Update database
            stock = Stock.objects.get(symbol=symbol)
            now = timezone.now()
            
            with transaction.atomic():
                # Create new price record and update stock
                stock_price = StockPrice.objects.create(
                    stock=stock,
                    price=quote_data['price'],
                    open_price=quote_data.get('open'),
                    high_price=quote_data.get('high'),
                    close_price=quote_data['price'],
                    low_price=quote_data.get('low'),
                    volume=quote_data.get('volume'),
                    timestamp=now
                )
                
                # Update stock's current price
                Stock.objects.filter(id=stock.id).update(
                    current_price=quote_data['price'],
                    last_updated=now
                )
            
            logger.info(f"Successfully updated {symbol}: ${quote_data['price']}")
            return stock_price
                
        except Stock.DoesNotExist:
            logger.error(f"Stock {symbol} not found")
            return None
        except requests.RequestException as e:
            logger.error(f"API request failed for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to update {symbol}: {e}")
            return None


