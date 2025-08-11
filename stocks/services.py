import requests
import time
import logging
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from .models import Stock, StockPrice, APIRequestLog

logger = logging.getLogger(__name__)


class StockDataService:
    """Simplified service for fetching stock data with basic rate limiting"""
    
    def __init__(self):
        self.api_key = settings.TWELVE_DATA_API_KEY
        self.base_url = "https://api.twelvedata.com"
        
    def fetch_quote(self, symbol):
        """Fetch detailed quote for a stock symbol"""
        try:
            url = f"{self.base_url}/quote"
            params = {
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            logger.info(f"Fetching quote for {symbol}")
            
            # Log API request for tracking
            self._log_api_request('quote')
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for rate limit error
            if isinstance(data, dict) and data.get('code') == 429:
                logger.error(f"Rate limit exceeded for {symbol}")
                return None
            
            # Parse successful response
            if 'close' in data:
                return {
                    'price': Decimal(str(data.get('close', 0))),
                    'open': Decimal(str(data.get('open', 0))) if data.get('open') else None,
                    'high': Decimal(str(data.get('high', 0))) if data.get('high') else None,
                    'low': Decimal(str(data.get('low', 0))) if data.get('low') else None,
                    'volume': int(data.get('volume', 0)) if data.get('volume') else None,
                }
            else:
                logger.error(f"Invalid response for {symbol}: {data}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"API request failed for {symbol}: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Data parsing error for {symbol}: {e}")
            return None

    def _log_api_request(self, endpoint):
        """Log API request for usage tracking"""
        try:
            from .models import APIRequestLog
            today = timezone.now().date()
            log, created = APIRequestLog.objects.get_or_create(
                endpoint=endpoint,
                date=today,
                defaults={'request_count': 0}
            )
            log.request_count += 1
            log.save()
            logger.info(f"API request logged: {endpoint} (count: {log.request_count})")
        except Exception as e:
            logger.error(f"Failed to log API request: {e}")


def update_stock_price(symbol, quote_data):
    """Update stock price in database"""
    try:
        stock = Stock.objects.get(symbol=symbol)
        
        stock_price = StockPrice.objects.create(
            stock=stock,
            price=quote_data['price'],
            open_price=quote_data.get('open'),
            high_price=quote_data.get('high'),
            low_price=quote_data.get('low'),
            volume=quote_data.get('volume'),
            timestamp=timezone.now()
        )
        
        # Update stock's current price
        stock.current_price = quote_data['price']
        stock.last_updated = timezone.now()
        stock.save()
        
        logger.info(f"Updated price for {symbol}: ${quote_data['price']}")
        return stock_price
        
    except Stock.DoesNotExist:
        logger.error(f"Stock {symbol} not found")
        return None
    except Exception as e:
        logger.error(f"Failed to update price for {symbol}: {e}")
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
