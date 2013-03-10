#!/usr/bin/env python

DEBUG = False
DEV = False

DATABASE_URL = 'sqlite:///expenses.db'

AVATAR_WIDTH = 72
AVATAR_HEIGHT = AVATAR_WIDTH
AVATAR_PLACEHOLD = "http://www.placehold.it/{width}x{height}/EFEFEF/AAAAAA&text=no+image".format(
        width=AVATAR_WIDTH, height=AVATAR_HEIGHT)

PERIOD_FORMAT = '%Y-%m'
DATE_FORMAT = '%Y-%m-%d'
DATE_US_FORMAT = '%m/%d/%Y'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

UPLOAD_DIR = 'static/uploads'
AVATAR_DIR = 'static/avatars'
EXPORT_DIR = 'static/exports'

EPOCH = '1970-01-01 00:00:00.000000'

DEFAULT_STATS_BINS = 30

COOKIE_EXPIRATION = 60 * 60 * 24 * 7 # Seven days

CATEGORY_FOREGROUND = '#333333'
CATEGORY_BACKGROUND = '#cccccc'

try:
    from local_config import *
except:
    pass
