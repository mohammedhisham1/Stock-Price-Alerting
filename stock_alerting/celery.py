import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_alerting.settings')

app = Celery('stock_alerting')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure periodic tasks
from celery.schedules import crontab

app.conf.beat_schedule = {
    'fetch-stock-prices': {
        'task': 'stocks.tasks.fetch_all_stock_prices',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'evaluate-alerts': {
        'task': 'alerts.tasks.evaluate_all_alerts', 
        'schedule': crontab(minute='*/5'),   # Every 5 minutes
    },
    'cleanup-old-data': {
        'task': 'stocks.tasks.cleanup_old_price_data',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'cleanup-old-alerts': {
        'task': 'stocks.tasks.cleanup_old_alerts',
        'schedule': crontab(hour=2, minute=30),  # Daily at 2:30 AM
    },
}

app.conf.timezone = 'UTC'


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
