#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime as datetime_

from config import DATE_FORMAT
from config import DATETIME_FORMAT


def date(value):
    return datetime_.strftime(value, DATETIME_FORMAT)


def datetime(value):
    return datetime_.strftime(value, DATE_FORMAT)
