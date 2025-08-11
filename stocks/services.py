import requests
import logging
import time
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.cache import cache
from .models import Stock, StockPrice, APIRequestLog

logger = logging.getLogger(__name__)


class StockDataService:
    """Service class for fetching stock data from external APIs with rate limiting"""
    
    def __init__(self):
        self.api_key = settings.TWELVE_DATA_API_KEY
        self.base_url = "https://api.twelvedata.com"
        self.rate_limit_key = "twelvedata_rate_limit"
        self.max_calls_per_minute = 7 
    
    def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        now = timezone.now()
        minute_key = f"{self.rate_limit_key}_{now.strftime('%Y%m%d_%H%M')}"
        
        current_calls = cache.get(minute_key, 0)
        
        if current_calls >= self.max_calls_per_minute:
            logger.warning(f"Rate limit reached: {current_calls}/{self.max_calls_per_minute} calls this minute")
            # Wait until next minute
            seconds_to_wait = 60 - now.second + 1
            logger.info(f"Waiting {seconds_to_wait} seconds for rate limit reset")
            time.sleep(seconds_to_wait)
            # Reset counter for new minute
            new_minute_key = f"{self.rate_limit_key}_{timezone.now().strftime('%Y%m%d_%H%M')}"
            cache.set(new_minute_key, 0, 60)
            current_calls = 0
        
        # Increment counter
        cache.set(minute_key, current_calls + 1, 60)
        return True
    
    def fetch_real_time_price(self, symbol):
        """Fetch real-time price for a single stock"""
        try:
            # Check rate limit before making request
            self._check_rate_limit()
            
            url = f"{self.base_url}/price"
            params = {
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            # Log API request
            self._log_api_request('price')
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'price' in data:
                return Decimal(str(data['price']))
            else:
                logger.error(f"No price data returned for {symbol}: {data}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"API request failed for {symbol}: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Invalid response data for {symbol}: {e}")
            return None
    
    def fetch_quote(self, symbol):
        """Fetch detailed quote information for a stock"""
        try:
            # Check rate limit before making request
            self._check_rate_limit()
            
            url = f"{self.base_url}/quote"
            params = {
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            # Log API request
            self._log_api_request('quote')
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'close' in data:
                return {
                    'price': Decimal(str(data.get('close', 0))),
                    'open': Decimal(str(data.get('open', 0))) if data.get('open') else None,
                    'high': Decimal(str(data.get('high', 0))) if data.get('high') else None,
                    'low': Decimal(str(data.get('low', 0))) if data.get('low') else None,
                    'volume': int(data.get('volume', 0)) if data.get('volume') else None,
                }
            else:
                logger.error(f"No quote data returned for {symbol}: {data}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"API request failed for {symbol}: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Invalid response data for {symbol}: {e}")
            return None
    
    def fetch_multiple_quotes(self, symbols):
        """Fetch quotes for multiple symbols - use batch when possible, individual with rate limiting otherwise"""
        try:
            # For free tier, batch requests might not work well, so use individual requests with rate limiting
            results = {}
            
            logger.info(f"Fetching quotes for {len(symbols)} symbols with rate limiting")
            
            for i, symbol in enumerate(symbols):
                try:
                    # Add delay between requests to respect rate limits
                    if i > 0:
                        time.sleep(10)  # 10 second delay between calls (6 calls per minute max)
                    
                    quote_data = self.fetch_quote(symbol)
                    if quote_data:
                        results[symbol] = quote_data
                    else:
                        logger.warning(f"No data retrieved for {symbol}")
                        
                except Exception as e:
                    logger.error(f"Error fetching {symbol}: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(results)} out of {len(symbols)} quotes")
            return results
            
        except Exception as e:
            logger.error(f"Batch quote fetch failed: {e}")
            return {}
    
    def _parse_quote_data(self, data):
        """Parse quote data from API response"""
        try:
            return {
                'price': Decimal(str(data.get('close', 0))),
                'open': Decimal(str(data.get('open', 0))) if data.get('open') else None,
                'high': Decimal(str(data.get('high', 0))) if data.get('high') else None,
                'low': Decimal(str(data.get('low', 0))) if data.get('low') else None,
                'volume': int(data.get('volume', 0)) if data.get('volume') else None,
            }
        except (ValueError, TypeError):
            return None
    
    def _log_api_request(self, endpoint):
        """Log API request for rate limiting tracking"""
        try:
            today = timezone.now().date()
            log, created = APIRequestLog.objects.get_or_create(
                endpoint=endpoint,
                date=today,
                defaults={'request_count': 0}
            )
            log.request_count += 1
            log.save()
        except Exception as e:
            logger.error(f"Failed to log API request: {e}")
    
    def get_daily_request_count(self, endpoint=None):
        """Get today's request count for an endpoint or all endpoints"""
        today = timezone.now().date()
        if endpoint:
            try:
                log = APIRequestLog.objects.get(endpoint=endpoint, date=today)
                return log.request_count
            except APIRequestLog.DoesNotExist:
                return 0
        else:
            logs = APIRequestLog.objects.filter(date=today)
            return sum(log.request_count for log in logs)


def update_stock_price(symbol, quote_data):
    """Update stock price in database"""
    try:
        stock = Stock.objects.get(symbol=symbol)
        
        # Create new price record
        stock_price = StockPrice.objects.create(
            stock=stock,
            price=quote_data['price'],
            open_price=quote_data.get('open'),
            high_price=quote_data.get('high'),
            low_price=quote_data.get('low'),
            close_price=quote_data['price'],  # Use current price as close
            volume=quote_data.get('volume'),
            timestamp=timezone.now()
        )
        
        logger.info(f"Updated price for {symbol}: ${quote_data['price']}")
        return stock_price
        
    except Stock.DoesNotExist:
        logger.error(f"Stock {symbol} not found in database")
        return None
    except Exception as e:
        logger.error(f"Failed to update price for {symbol}: {e}")
        return None


def initialize_monitored_stocks():
    """Initialize the stocks we want to monitor"""
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
