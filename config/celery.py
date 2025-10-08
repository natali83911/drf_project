from __future__ import absolute_import, unicode_literals

import eventlet

eventlet.monkey_patch()


import os

from celery import Celery

# Установка переменной окружения для настроек проекта
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Создание экземпляра Celery
app = Celery("config")

# Загрузка настроек из Django с префиксом CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматическое обнаружение задач в файлах tasks.py каждого приложения
app.autodiscover_tasks()
