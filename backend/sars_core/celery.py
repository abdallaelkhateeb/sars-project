import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sars_core.settings.dev")

app = Celery("sars_core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
