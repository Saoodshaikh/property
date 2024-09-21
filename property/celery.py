from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default django setting module for the 'celery' programe

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property.settings')

app = Celery('property')

# Load task module for all registered Django app configs

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()