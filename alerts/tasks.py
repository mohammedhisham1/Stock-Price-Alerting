from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template import Context, Template
import logging
from celery import group


from .models import Alert, TriggeredAlert, NotificationTemplate
from stocks.models import StockPrice

logger = logging.getLogger(__name__)


@shared_task
def evaluate_alert(alert_id):
    """Evaluate a single alert"""
    try:
        alert = Alert.objects.get(id=alert_id, is_active=True)
        latest_price = StockPrice.get_latest_price(alert.stock.symbol)
        
        if latest_price is None:
            logger.warning(f"No price data available for {alert.stock.symbol}")
            return {
                'alert_id': alert_id,
                'success': False,
                'error': 'No price data available'
            }
        
        should_trigger = alert.should_trigger(latest_price)
        
        if should_trigger:
            # Create triggered alert record
            triggered_alert = TriggeredAlert.objects.create(
                alert=alert,
                trigger_price=latest_price
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
                'trigger_price': float(latest_price),
                'triggered_alert_id': triggered_alert.id
            }
        
        return {
            'alert_id': alert_id,
            'success': True,
            'triggered': False,
            'current_price': float(latest_price)
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
            return {
                'triggered_alert_id': triggered_alert_id,
                'success': False,
                'error': 'No email address'
            }
        
        # Get notification template
        try:
            template = NotificationTemplate.objects.get(
                template_type=alert.alert_type,
                is_active=True
            )
        except NotificationTemplate.DoesNotExist:
            # Use default template
            template = create_default_template(alert.alert_type)
        
        # Prepare template context
        context = {
            'user_name': user.first_name or user.username,
            'stock_symbol': alert.stock.symbol,
            'stock_name': alert.stock.name,
            'condition': alert.condition,
            'threshold_price': alert.threshold_price,
            'trigger_price': triggered_alert.trigger_price,
            'triggered_at': triggered_alert.triggered_at,
            'alert_type': alert.alert_type,
            'duration_minutes': alert.duration_minutes if alert.alert_type == 'duration' else None,
        }
        
        # Render subject and content
        subject_template = Template(template.subject)
        text_template = Template(template.text_content)
        html_template = Template(template.html_content)
        
        subject = subject_template.render(Context(context))
        text_content = text_template.render(Context(context))
        html_content = html_template.render(Context(context))
        
        # Send email
        send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False
        )
        
        # Update triggered alert
        triggered_alert.email_sent = True
        triggered_alert.email_sent_at = timezone.now()
        triggered_alert.save()
        
        logger.info(f"Alert notification sent to {user.email} for {alert}")
        
        return {
            'triggered_alert_id': triggered_alert_id,
            'success': True,
            'email_sent': True,
            'recipient': user.email
        }
        
    except TriggeredAlert.DoesNotExist:
        logger.error(f"Triggered alert {triggered_alert_id} not found")
        return {
            'triggered_alert_id': triggered_alert_id,
            'success': False,
            'error': 'Triggered alert not found'
        }
    except Exception as e:
        logger.error(f"Error sending notification for triggered alert {triggered_alert_id}: {e}")
        
        # Update triggered alert with error
        try:
            triggered_alert = TriggeredAlert.objects.get(id=triggered_alert_id)
            triggered_alert.notification_error = str(e)
            triggered_alert.save()
        except TriggeredAlert.DoesNotExist:
            pass
        
        return {
            'triggered_alert_id': triggered_alert_id,
            'success': False,
            'error': str(e)
        }


@shared_task
def cleanup_old_triggered_alerts(days_to_keep=30):
    """Clean up old triggered alert records"""
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days_to_keep)
        deleted_count, _ = TriggeredAlert.objects.filter(
            triggered_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old triggered alert records")
        
        return {
            'success': True,
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up triggered alerts: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def create_default_template(template_type):
    """Create default notification template"""
    if template_type == 'threshold':
        subject = "Stock Alert: {{stock_symbol}} {{condition}} ${{threshold_price}}"
        text_content = """
Hello {{user_name}},

Your stock alert has been triggered!

Stock: {{stock_symbol}} ({{stock_name}})
Alert: Price {{condition}} ${{threshold_price}}
Current Price: ${{trigger_price}}
Triggered At: {{triggered_at}}

This is an automated message from Stock Price Alerting System.
        """.strip()
        html_content = """
<h2>Stock Alert Triggered</h2>
<p>Hello {{user_name}},</p>
<p>Your stock alert has been triggered!</p>
<ul>
<li><strong>Stock:</strong> {{stock_symbol}} ({{stock_name}})</li>
<li><strong>Alert:</strong> Price {{condition}} ${{threshold_price}}</li>
<li><strong>Current Price:</strong> ${{trigger_price}}</li>
<li><strong>Triggered At:</strong> {{triggered_at}}</li>
</ul>
<p>This is an automated message from Stock Price Alerting System.</p>
        """.strip()
    
    else:  # duration
        subject = "Stock Alert: {{stock_symbol}} {{condition}} ${{threshold_price}} for {{duration_minutes}} minutes"
        text_content = """
Hello {{user_name}},

Your duration stock alert has been triggered!

Stock: {{stock_symbol}} ({{stock_name}})
Alert: Price {{condition}} ${{threshold_price}} for {{duration_minutes}} minutes
Current Price: ${{trigger_price}}
Triggered At: {{triggered_at}}

This is an automated message from Stock Price Alerting System.
        """.strip()
        html_content = """
<h2>Duration Stock Alert Triggered</h2>
<p>Hello {{user_name}},</p>
<p>Your duration stock alert has been triggered!</p>
<ul>
<li><strong>Stock:</strong> {{stock_symbol}} ({{stock_name}})</li>
<li><strong>Alert:</strong> Price {{condition}} ${{threshold_price}} for {{duration_minutes}} minutes</li>
<li><strong>Current Price:</strong> ${{trigger_price}}</li>
<li><strong>Triggered At:</strong> {{triggered_at}}</li>
</ul>
<p>This is an automated message from Stock Price Alerting System.</p>
        """.strip()
    
    template, created = NotificationTemplate.objects.get_or_create(
        template_type=template_type,
        defaults={
            'subject': subject,
            'text_content': text_content,
            'html_content': html_content,
            'is_active': True
        }
    )
    
    return template
