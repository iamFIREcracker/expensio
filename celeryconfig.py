#!/usr/bin/env python
# -*- coding: utf-8 -*-

BROKER_URL = 'amqp://expenses:expenses@localhost:5672'

CELERY_IMPORTS = ('app.tasks',)

CELERY_RESULT_BACKEND = 'amqp'
CELERY_RESULT_DBURI = 'amqp://expenses:expenses@localhost:5672'


try:
    from local_celeryconfig import *
except ImportError:
    pass
