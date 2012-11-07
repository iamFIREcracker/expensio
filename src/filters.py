#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime


def datetimeformat(value, today=datetime.today(), format_=None):
    delta = today - value
    within24 = (delta.total_seconds() // 3600) < 24
    sameyear = today.year == value.year

    if format_:
        return value.strftime(format_)
    elif within24:
        return value.strftime('%I:%M %p')
    elif sameyear:
        return value.strftime('%b %-d')
    else:
        return value.strftime('%d/%m/%y')


def cashformat(value):
    return "{:,.2f}".format(value)
