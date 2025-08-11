import time
import logging
from decimal import Decimal
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Stock, StockPrice
from alerts.models import Alert, TriggeredAlert
from .services import StockDataService, update_stock_price

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
            
            # Fetch quote data
            quote_data = service.fetch_quote(stock.symbol)
            
            if quote_data:
                # Update database
                if update_stock_price(stock.symbol, quote_data):
                    success_count += 1
                    logger.info(f"✅ Updated {stock.symbol}: ${quote_data['price']}")
                else:
                    error_count += 1
                    logger.error(f"❌ Failed to update {stock.symbol} in database")
            else:
                error_count += 1
                logger.error(f"❌ No data received for {stock.symbol}")
            
            # Rate limiting: Wait between requests (except after last stock)
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
def evaluate_price_alerts():
    """Check all active alerts and send notifications if conditions are met"""
    try:
        active_alerts = Alert.objects.filter(
            is_active=True,
            stock__is_active=True
        ).select_related('stock', 'user')
        
        if not active_alerts.exists():
            logger.info("No active alerts to evaluate")
            return {"success": True, "message": "No active alerts"}
        
        triggered_count = 0
        
        for alert in active_alerts:
            try:
                current_price = alert.stock.current_price
                
                if not current_price:
                    logger.warning(f"No current price for {alert.stock.symbol}")
                    continue
                
                # Check if alert condition is met
                should_trigger = False
                
                if alert.condition == 'above' and current_price >= alert.threshold_price:
                    should_trigger = True
                elif alert.condition == 'below' and current_price <= alert.threshold_price:
                    should_trigger = True
                
                if should_trigger:
                    # Create triggered alert record
                    TriggeredAlert.objects.create(
                        alert=alert,
                        trigger_price=current_price
                    )
                    
                    # Deactivate the alert (one-time trigger)
                    alert.is_active = False
                    alert.save()
                    
                    triggered_count += 1
                    logger.info(f"🔔 Triggered alert for {alert.stock.symbol}: ${current_price}")
                
            except Exception as e:
                logger.error(f"Error evaluating alert for {alert.stock.symbol}: {e}")
                continue
        
        logger.info(f"Evaluated alerts: {triggered_count} triggered")
        
        return {
            "success": True,
            "evaluated": active_alerts.count(),
            "triggered": triggered_count
        }
        
    except Exception as e:
        logger.error(f"Alert evaluation failed: {e}")
        return {"success": False, "error": str(e)}


@shared_task
def cleanup_old_price_data():
    """Remove stock price data older than 30 days"""
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
    """Remove triggered alerts older than 7 days"""
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
