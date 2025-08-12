import requests
import logging
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from .models import Stock, StockPrice

logger = logging.getLogger(__name__)


class StockDataService:
    """Service for fetching stock data with rate limiting"""
    
    def __init__(self):
        self.api_key = settings.TWELVE_DATA_API_KEY
        self.base_url = "https://api.twelvedata.com"
        
    def fetch_and_update_stock(self, symbol):
        """Fetch quote and update stock price in database"""
        try:
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


def initialize_monitored_stocks():
    """Initialize default stocks to monitor"""
    stock_data = [
        ('AAPL', 'Apple Inc.', 'NASDAQ'),
        ('TSLA', 'Tesla Inc.', 'NASDAQ'),
        ('GOOGL', 'Alphabet Inc.', 'NASDAQ'),
        ('AMZN', 'Amazon.com Inc.', 'NASDAQ'),
        ('MSFT', 'Microsoft Corporation', 'NASDAQ'),
        ('META', 'Meta Platforms Inc.', 'NASDAQ'),
        ('NVDA', 'NVIDIA Corporation', 'NASDAQ'),
        ('NFLX', 'Netflix Inc.', 'NASDAQ'),
        ('UBER', 'Uber Technologies Inc.', 'NYSE'),
        ('SPOT', 'Spotify Technology S.A.', 'NYSE'),
    ]
    
    created_count = 0
    for symbol, name, exchange in stock_data:
        stock, created = Stock.objects.get_or_create(
            symbol=symbol,
            defaults={
                'name': name,
                'exchange': exchange,
                'is_active': True
            }
        )
        if created:
            created_count += 1
            logger.info(f"Created stock: {symbol} - {name}")
    
    logger.info(f"Initialized {created_count} new stocks")
    return created_count
