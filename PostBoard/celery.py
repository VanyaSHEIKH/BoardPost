import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PostBoard.settings')

app = Celery('PostBoard')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'action_every_monday_8am': {
        'task': 'main.tasks.send_weekly_celery',
        'schedule': crontab(hour=6, minute=55, day_of_week='thursday'),
        'args': ()
    },
}
