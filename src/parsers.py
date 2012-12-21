#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime as datetime_

from config import DATE_FORMAT
from config import DATETIME_FORMAT
from config import PERIOD_FORMAT


def amount(value):
    return float(value)

def currency(value):
    if value not in ['€', '$']:
        raise ValueError()
    else:
        return value

def date(value):
    return datetime_.strptime(value, DATETIME_FORMAT)

def datetime(value):
    return datetime_.strptime(value, DATE_FORMAT)

def period(value):
    return datetime_.strptime(value, PERIOD_FORMAT)
