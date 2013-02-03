#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import 

from celery import Celery


celery = Celery('app.celery',
                broker='amqp://expenses:expenses@localhost:5672//',
                backend='amqp',
                include=('app.tasks',))

celery.conf.update(
    CELERY_RESULT_DBURI='sqlite:///celery.db'
)
