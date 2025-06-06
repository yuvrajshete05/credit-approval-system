from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set default Django settings module for 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_approval_system.settings')

# Create Celery app instance
app = Celery('credit_approval_system')

# Load config from Django settings with CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in installed apps
app.autodiscover_tasks()

# Broker URL (optional here if you set in settings.py, but okay to keep)
app.conf.broker_url = 'redis://localhost:6379/0'
