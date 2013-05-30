#!/usr/bin/env bash

cat > local_config.py <<!
DEV = True

DEBUG = False
DEBUG_SQL = False

LOG_ENABLE = False

DATABASE_URL = 'sqlite:///appdb.sqlite'
!

nosetests --with-doctest app tests
