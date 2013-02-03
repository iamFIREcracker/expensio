#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import 

from celery import Celery


celery = Celery('app.celery',
                broker='sqla+sqlite:///celery.db',
                backend='database',
                include=('app.tasks',))

celery.conf.update(
    CELERY_RESULT_DBURI='sqlite:///celery.db'
)
