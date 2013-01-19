#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime as datetime_

import config
import utils


def amount(value):
    return float(value)

def currency(value):
    if value not in utils.currencies():
        raise ValueError()
    else:
        return value

def expenses(period, data):
    expenses = []

    for line in data.split('\r\n'):
        (date_, category_, amount_, note_) = line.split('\t')

        expenses.append((
            date('-'.join([period, date_])),
            category_, amount(amount_), note_,))
    return expenses

def date(value):
    return datetime_.strptime(value, config.DATE_FORMAT)

def date_us(value):
    return datetime_.strptime(value, config.DATE_US_FORMAT)

def datetime(value):
    return datetime_.strptime(value, config.DATETIME_FORMAT)

def period(value):
    return datetime_.strptime(value, config.PERIOD_FORMAT)

def period_us(value):
    return datetime_.strptime(value, config.PERIOD_US_FORMAT)
