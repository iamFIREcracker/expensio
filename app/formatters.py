#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime as datetime_

from config import DATE_FORMAT
from config import DATETIME_FORMAT


def amount(value):
    #return "{:,.2f}".format(value)
    return value


def date(value):
    return datetime_.strftime(value, DATE_FORMAT)


def datetime(value):
    return datetime_.strftime(value, DATETIME_FORMAT)
