#!/usr/bin/env python

import os


DATABASE_ENGINE = 'sqlite:///' + os.path.join(
    os.path.dirname(__file__), 'mytestdatabase.db')

DATABASE_SESSION_ENGINE = 'sqlite:///' + os.path.join(
    os.path.dirname(__file__), 'sessions.db')

PERIOD_FORMAT = '%Y-%m'
DATETIME_FORMAT = '%Y-%m-%d'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

UPLOAD_DIR = 'static/uploads'

EPOCH = '1970-01-01 00:00:00.000000'

COOKIE_EXPIRATION = 60 * 60 * 24 * 7 # Seven days
