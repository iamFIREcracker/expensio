#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime as datetime_

import config


def amount(value):
    #return "{:,.2f}".format(value)
    return value


def date(value):
    return datetime_.strftime(value, config.DATE_FORMAT)


def date_us(value):
    return datetime_.strftime(value, config.DATE_US_FORMAT)


def datetime(value):
    return datetime_.strftime(value, config.DATETIME_FORMAT)


def period(value):
    return datetime_.strftime(value, config.PERIOD_FORMAT)

def yearday(value):
    if value:
        return period(value)

def monthday(value):
    if value:
        return int(value)
