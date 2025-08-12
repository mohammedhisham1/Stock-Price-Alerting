import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_alerting.settings')

app = Celery('stock_alerting')

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
        'schedule': crontab(day_of_month=1, hour=2, minute=0),  # Monthly on 1st at 2 AM
    },
    'cleanup-old-alerts': {
        'task': 'stocks.tasks.cleanup_old_alerts',
        'schedule': crontab(day_of_month=1, hour=2, minute=30),  # Monthly on 1st at 2:30 AM
    },
}

app.conf.timezone = 'UTC'


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
