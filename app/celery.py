#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import 

import web
from celery import Celery


celery = Celery('app.celery',
                broker=web.config.celery_broker,
                backend=web.config.celery_broker_backend,
                include=('app.tasks',))

#celery.conf.update(
    #CELERY_ALWAYS_EAGER=web.config.celery_always_eager
#)
