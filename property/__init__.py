from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when django starts so shared tasks will use this app

from .celery import app 

__all__ = ('celery_app')