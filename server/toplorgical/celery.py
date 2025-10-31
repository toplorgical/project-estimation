import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toplorgical.settings')

app = Celery('toplorgical')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure beat schedule
app.conf.beat_schedule = {
    'update-prices-daily': {
        'task': 'pricing.tasks.update_all_prices',
        'schedule': 86400.0,  # Run every 24 hours
    },
    'scrape-materials-daily': {
        'task': 'pricing.tasks.trigger_scraping',
        'schedule': 86400.0,  # Run every 24 hours
    },
}

app.conf.timezone = 'UTC'