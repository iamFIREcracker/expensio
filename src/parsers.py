#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime as datetime_

from config import DATE_FORMAT
from config import LATEST_DAYS_DATE_FORMAT


def date(value):
    return datetime_.strptime(value, LATEST_DAYS_DATE_FORMAT)

def datetime(value):
    return datetime_.strptime(value, DATE_FORMAT)
