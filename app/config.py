#!/usr/bin/env python


DATABASE_URL = 'sqlite:///expenses.db'

PERIOD_FORMAT = '%Y-%m'
DATE_FORMAT = '%Y-%m-%d'
DATE_US_FORMAT = '%m/%d/%Y'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

UPLOAD_DIR = 'static/uploads'

EXPORT_DIR = 'static/exports'

EPOCH = '1970-01-01 00:00:00.000000'

COOKIE_EXPIRATION = 60 * 60 * 24 * 7 # Seven days
