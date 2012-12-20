#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime as datetime_

from config import DATE_FORMAT
from config import DATETIME_FORMAT


def amount(value):
    return float(value)

def date(value):
    return datetime_.strptime(value, DATETIME_FORMAT)

def datetime(value):
    return datetime_.strptime(value, DATE_FORMAT)
