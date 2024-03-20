from __future__ import absolute_import

import os
import django

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyFavouriteAndShippingAddress.settings')
django.setup()

app = Celery('MyFavouriteAndShippingAddress')

app.conf.enable_utc = False
app.conf.update(timezone='Asia/Tashkent')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'apply_discount': {
        'task': 'main.tasks.apply_discount',
        'schedule': 5
    },
    'remove_discount': {
        'task': 'main.tasks.remove_discount',
        'schedule': 5
    }
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')