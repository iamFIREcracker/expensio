#!/usr/bin/env python

APP_NAME = 'expenses'

LOGGER_NAME = APP_NAME
LOG_FORMAT = '[%(process)d] %(levelname)s %(message)s [in %(pathname)s:%(lineno)d]'

DEBUG = False
DEBUG_SQL = False

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
CATEGORY_BACKGROUND = '#e6e6e6'
CATEGORY_PALETTE = [
        {'foreground': '#ffffff', 'background': '#3366cc' },
        {'foreground': '#ffffff', 'background': '#dc3912' },
        {'foreground': '#ffffff', 'background': '#ff9900' },
        {'foreground': '#ffffff', 'background': '#109618' },
        {'foreground': '#ffffff', 'background': '#990099' },
        {'foreground': '#ffffff', 'background': '#0099c6' },
        {'foreground': '#ffffff', 'background': '#dd4477' },
        {'foreground': '#ffffff', 'background': '#66aa00' },
        {'foreground': '#ffffff', 'background': '#b82e2e' },
        {'foreground': '#ffffff', 'background': '#316395' },
        {'foreground': '#ffffff', 'background': '#994499' },
        {'foreground': '#ffffff', 'background': '#22aa99' },
        {'foreground': '#ffffff', 'background': '#aaaa11' },
        {'foreground': '#ffffff', 'background': '#6633cc' },
        {'foreground': '#ffffff', 'background': '#e67300' },
        {'foreground': '#ffffff', 'background': '#8b0707' },
        {'foreground': '#ffffff', 'background': '#651067' },
        {'foreground': '#ffffff', 'background': '#329262' },
        {'foreground': '#ffffff', 'background': '#5574a6' },
        {'foreground': '#ffffff', 'background': '#3b3eac' },
        {'foreground': '#ffffff', 'background': '#b77322' },
        {'foreground': '#ffffff', 'background': '#16d620' },
        {'foreground': '#ffffff', 'background': '#b91383' },
        {'foreground': '#ffffff', 'background': '#f4359e' },
        {'foreground': '#ffffff', 'background': '#9c5935' },
        {'foreground': '#ffffff', 'background': '#a9c413' }
    ]

try:
    from local_config import *
except:
    pass
