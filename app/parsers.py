#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime as datetime_

from config import DATE_FORMAT
from config import DATETIME_FORMAT
from config import PERIOD_FORMAT


def amount(value):
    return float(value)

def currency(value):
    if value not in [u'€', u'$']:
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
    return datetime_.strptime(value, DATETIME_FORMAT)

def datetime(value):
    return datetime_.strptime(value, DATE_FORMAT)

def period(value):
    return datetime_.strptime(value, PERIOD_FORMAT)
