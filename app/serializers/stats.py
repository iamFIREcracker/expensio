#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import formatters


class StatByCategorySerializer(object):
    
    def __init__(self, category, currency):
        self.o = category
        self.currency = currency

    def to_dict(self):
        return {
            'name': self.o[0],
            'updated': formatters.datetime(self.o[1]),
            'income': formatters.amount(self.o[2]),
            'outcome': formatters.amount(self.o[3]),
            'currency': self.currency,
        }


class StatByDaySerializer(object):
    
    def __init__(self, day, currency):
        self.o = day
        self.currency = currency

    def to_dict(self):
        return {
            'date': formatters.date(self.o['date']),
            'income': formatters.amount(self.o['income']),
            'outcome': formatters.amount(self.o['outcome']),
            'currency': self.currency,
        }
