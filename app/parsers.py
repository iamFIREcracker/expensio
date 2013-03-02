#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime as datetime_

import web

import config
import utils


def amount(value):
    return float(value)

def currency(value):
    if value not in utils.currencies():
        raise ValueError()
    else:
        return value

def format(value):
    if value not in utils.formats():
        raise ValueError()
    else:
        return value

def yearday(value):
    if value:
        return datetime_.strptime(value, config.YEARLY_FORMAT)

def monthday(value):
    if value:
        value = int(value)
        if value not in utils.monthdays():
            raise ValueError()
        return value

def weekday(value):
    if value:
        if value not in utils.weekdays():
            raise ValueError()
        return value

def expenses(data):
    expenses = []

    for line in data.split('\n'):
        if line:
            (date_, category_, amount_, note_) = line.split('\t')
            expenses.append(( date_us(date_), category_, amount(amount_), note_,))
    return expenses

def date(value):
    return datetime_.strptime(value, config.DATE_FORMAT)

def date_us(value):
    return datetime_.strptime(value, config.DATE_US_FORMAT)

def datetime(value):
    return datetime_.strptime(value, config.DATETIME_FORMAT)

def period(value):
    return datetime_.strptime(value, config.PERIOD_FORMAT)
