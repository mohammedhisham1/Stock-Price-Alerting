import time
import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Stock, StockPrice
from alerts.models import TriggeredAlert
from .services import StockDataService

logger = logging.getLogger(__name__)


@shared_task
def fetch_all_stock_prices():
    """Fetch current prices for all active stocks with proper rate limiting"""
    service = StockDataService()
    active_stocks = Stock.objects.filter(is_active=True)
    
    if not active_stocks.exists():
        logger.info("No active stocks to fetch")
        return {"success": True, "message": "No active stocks"}
    
    logger.info(f"Starting price fetch for {active_stocks.count()} stocks")
    
    success_count = 0
    error_count = 0
    
    for i, stock in enumerate(active_stocks):
        try:
            logger.info(f"Processing {i+1}/{active_stocks.count()}: {stock.symbol}")
            
            # Fetch and update stock data in single operation
            result = service.fetch_and_update_stock(stock.symbol)
            
            if result:
                success_count += 1
                logger.info(f"✅ Updated {stock.symbol}")
            else:
                error_count += 1
                logger.error(f"❌ Failed to update {stock.symbol}")
            
            # Rate limiting: Wait between requests
            if i < active_stocks.count() - 1:
                logger.info("Waiting 10 seconds before next request...")
                time.sleep(10)
                
        except Exception as e:
            error_count += 1
            logger.error(f"❌ Exception processing {stock.symbol}: {e}")
            continue
    
    # Summary
    total_processed = success_count + error_count
    logger.info(f"Completed: {success_count} successful, {error_count} errors out of {total_processed}")
    
    return {
        "success": True,
        "processed": total_processed,
        "successful": success_count,
        "errors": error_count
    }


@shared_task
def cleanup_old_price_data():
    try:
        cutoff_date = timezone.now() - timedelta(days=30)
        
        old_prices = StockPrice.objects.filter(timestamp__lt=cutoff_date)
        count = old_prices.count()
        
        if count > 0:
            old_prices.delete()
            logger.info(f"Cleaned up {count} old price records")
        else:
            logger.info("No old price data to clean up")
        
        return {
            "success": True,
            "cleaned_records": count
        }
        
    except Exception as e:
        logger.error(f"Price data cleanup failed: {e}")
        return {"success": False, "error": str(e)}


@shared_task
def cleanup_old_alerts():
    try:
        cutoff_date = timezone.now() - timedelta(days=7)
        
        old_alerts = TriggeredAlert.objects.filter(
            triggered_at__lt=cutoff_date
        )
        
        count = old_alerts.count()
        
        if count > 0:
            old_alerts.delete()
            logger.info(f"Cleaned up {count} old triggered alerts")
        else:
            logger.info("No old triggered alerts to clean up")
        
        return {
            "success": True,
            "cleaned_alerts": count
        }
        
    except Exception as e:
        logger.error(f"Triggered alert cleanup failed: {e}")
        return {"success": False, "error": str(e)}
