from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging
from celery import group

from .models import Alert, TriggeredAlert

logger = logging.getLogger(__name__)

@shared_task
def evaluate_alert(alert_id):
    """Evaluate a single alert"""
    try:
        alert = Alert.objects.get(id=alert_id, is_active=True)
        current_price = alert.stock.current_price
        
        if current_price is None:
            logger.warning(f"No price data available for {alert.stock.symbol}")
            return {
                'alert_id': alert_id,
                'success': False,
                'error': 'No price data available'
            }
        
        should_trigger = alert.should_trigger(current_price)
        
        if should_trigger:
            # Create triggered alert record
            triggered_alert = TriggeredAlert.objects.create(
                alert=alert,
                trigger_price=current_price
            )
            
            # Send notification
            send_alert_notification.delay(triggered_alert.id)
            
            # Deactivate alert to prevent repeated triggers
            alert.is_active = False
            alert.save()
            
            logger.info(f"Alert triggered: {alert}")
            
            return {
                'alert_id': alert_id,
                'success': True,
                'triggered': True,
                'trigger_price': float(current_price),
                'triggered_alert_id': triggered_alert.id
            }
        
        return {
            'alert_id': alert_id,
            'success': True,
            'triggered': False,
            'current_price': float(current_price)
        }
        
    except Alert.DoesNotExist:
        logger.error(f"Alert {alert_id} not found")
        return {
            'alert_id': alert_id,
            'success': False,
            'error': 'Alert not found'
        }
    except Exception as e:
        logger.error(f"Error evaluating alert {alert_id}: {e}")
        return {
            'alert_id': alert_id,
            'success': False,
            'error': str(e)
        }

@shared_task
def evaluate_all_alerts():
    """Evaluate all active alerts concurrently"""
    try:
        active_alerts = Alert.objects.filter(is_active=True)
        if not active_alerts.exists():
            logger.info("No active alerts found.")
            return {
                'success': True,
                'total_alerts': 0,
                'triggered_count': 0,
                'results': [],
                'timestamp': timezone.now().isoformat()
            }

        tasks = group(evaluate_alert.s(alert.id) for alert in active_alerts)
        results = tasks.apply_async().get()  # wait for all tasks to complete

        triggered_count = sum(1 for result in results if result.get('triggered'))

        logger.info(f"Evaluated {len(active_alerts)} alerts, {triggered_count} triggered")

        return {
            'success': True,
            'total_alerts': len(active_alerts),
            'triggered_count': triggered_count,
            'results': results,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error evaluating all alerts: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task
def send_alert_notification(triggered_alert_id):
    """Send email notification for a triggered alert"""
    try:
        triggered_alert = TriggeredAlert.objects.get(id=triggered_alert_id)
        alert = triggered_alert.alert
        user = alert.user
        
        if not user.email:
            logger.warning(f"No email address for user {user.username}")
            triggered_alert.notification_error = "No email address"
            triggered_alert.save()
            return {'triggered_alert_id': triggered_alert_id, 'success': False, 'error': 'No email address'}
        
        # Simple email content
        if alert.alert_type == 'duration':
            subject = f"Stock Alert: {alert.stock.symbol} {alert.condition} ${alert.threshold_price} for {alert.duration_minutes} minutes"
            message = f"Your duration alert has been triggered!\n\nStock: {alert.stock.symbol} ({alert.stock.name})\nPrice {alert.condition} ${alert.threshold_price} for {alert.duration_minutes} minutes\nCurrent Price: ${triggered_alert.trigger_price}\nTriggered: {triggered_alert.triggered_at}"
        else:
            subject = f"Stock Alert: {alert.stock.symbol} {alert.condition} ${alert.threshold_price}"
            message = f"Your stock alert has been triggered!\n\nStock: {alert.stock.symbol} ({alert.stock.name})\nPrice {alert.condition} ${alert.threshold_price}\nCurrent Price: ${triggered_alert.trigger_price}\nTriggered: {triggered_alert.triggered_at}"
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        # Update triggered alert
        triggered_alert.email_sent = True
        triggered_alert.email_sent_at = timezone.now()
        triggered_alert.save()
        
        logger.info(f"Alert notification sent to {user.email} for {alert}")
        return {'triggered_alert_id': triggered_alert_id, 'success': True, 'email_sent': True, 'recipient': user.email}
        
    except TriggeredAlert.DoesNotExist:
        logger.error(f"Triggered alert {triggered_alert_id} not found")
        return {'triggered_alert_id': triggered_alert_id, 'success': False, 'error': 'Triggered alert not found'}
    except Exception as e:
        logger.error(f"Error sending notification for triggered alert {triggered_alert_id}: {e}")
        # Save error to triggered alert if it exists
        try:
            TriggeredAlert.objects.filter(id=triggered_alert_id).update(notification_error=str(e))
        except:
            pass
        return {'triggered_alert_id': triggered_alert_id, 'success': False, 'error': str(e)}
