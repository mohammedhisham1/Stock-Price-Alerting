from celery import shared_task
from django.conf import settings
from django.utils import timezone
import logging
import time
from .models import Stock, StockPrice
from .services import StockDataService, update_stock_price

logger = logging.getLogger(__name__)


@shared_task
def fetch_stock_price(symbol):
    """Fetch price for a single stock symbol"""
    try:
        service = StockDataService()
        quote_data = service.fetch_quote(symbol)
        
        if quote_data:
            stock_price = update_stock_price(symbol, quote_data)
            if stock_price:
                return {
                    'symbol': symbol,
                    'price': float(stock_price.price),
                    'timestamp': stock_price.timestamp.isoformat(),
                    'success': True
                }
        
        return {
            'symbol': symbol,
            'success': False,
            'error': 'Failed to fetch price data'
        }
        
    except Exception as e:
        logger.error(f"Task failed for {symbol}: {e}")
        return {
            'symbol': symbol,
            'success': False,
            'error': str(e)
        }


@shared_task
def fetch_all_stock_prices():
    """Fetch prices for all active monitored stocks with proper rate limiting"""
    try:
        active_stocks = Stock.objects.filter(is_active=True)
        symbols = list(active_stocks.values_list('symbol', flat=True))
        
        if not symbols:
            logger.warning("No active stocks to monitor")
            return {'success': False, 'error': 'No active stocks'}
        
        service = StockDataService()
        
        # Check daily API limit
        daily_requests = service.get_daily_request_count()
        logger.info(f"Daily API requests so far: {daily_requests}")
        
        # Use individual requests with proper rate limiting (no batch processing)
        results = []
        successful_updates = 0
        
        logger.info(f"Fetching prices for {len(symbols)} stocks with rate limiting...")
        
        for i, symbol in enumerate(symbols):
            try:
                # Add 10-second delay between each request to respect rate limits
                if i > 0:
                    logger.info(f"Waiting 10 seconds before fetching {symbol}...")
                    time.sleep(10)
                
                # Fetch quote for individual stock
                quote_data = service.fetch_quote(symbol)
                
                if quote_data:
                    stock_price = update_stock_price(symbol, quote_data)
                    if stock_price:
                        results.append({
                            'symbol': symbol,
                            'price': float(stock_price.price),
                            'success': True
                        })
                        successful_updates += 1
                        logger.info(f"Successfully updated {symbol}: ${stock_price.price}")
                    else:
                        results.append({
                            'symbol': symbol,
                            'success': False,
                            'error': 'Failed to update price in database'
                        })
                else:
                    results.append({
                        'symbol': symbol,
                        'success': False,
                        'error': 'Failed to fetch price'
                    })
                    
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                results.append({
                    'symbol': symbol,
                    'success': False,
                    'error': str(e)
                })
        
        logger.info(f"Updated prices for {successful_updates}/{len(symbols)} stocks")
        
        return {
            'success': True,
            'updated_count': successful_updates,
            'total_count': len(symbols),
            'results': results,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"fetch_all_stock_prices task failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def cleanup_old_stock_prices(days_to_keep=30):
    """Clean up old stock price records to manage database size"""
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days_to_keep)
        deleted_count, _ = StockPrice.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old stock price records")
        return {
            'success': True,
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"cleanup_old_stock_prices task failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }
