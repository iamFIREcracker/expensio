#!/usr/bin/env bash

set -e

cat > local_celeryconfig.py <<!
BROKER_BACKEND = 'sqlakombu.transport.Transport'
BROKER_HOST = 'sqlite:///celerydb.sqlite'

CELERY_RESULT_DBURI = 'sqlite:///celerydb.sqlite'

CELERY_IMPORTS = ('app.tasks',)

CELERYD_HIJACK_ROOT_LOGGER = False
!

cat > local_config.py <<!
DEV = True

DEBUG = False
DEBUG_SQL = False

LOG_ENABLE = False

DATABASE_URL = 'sqlite:///appdb.sqlite'
!

celery worker --app=app --loglevel=info >> /dev/null 2>> celery.log &

trap 'kill $(jobs -p); rm local_config.py local_celeryconfig.py' EXIT

nosetests --with-doctest app tests
