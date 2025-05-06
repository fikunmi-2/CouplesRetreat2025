from __future__ import  absolute_import, unicode_literals
import os
from celery import Celery

from retreat import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retreat.settings')

app = Celery('retreat')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.timezone = 'Africa/Lagos'


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')