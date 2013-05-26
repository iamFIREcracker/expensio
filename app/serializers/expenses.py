#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import formatters


class ExpenseSerializer(object):

    def __init__(self, expense, currency):
        self.o = expense
        self.currency = currency

    def to_dict(self):
        return {
            'id': self.o.id,
            'date': formatters.date(self.o.date),
            'created': formatters.datetime(self.o.created),
            'updated': formatters.datetime(self.o.updated),
            'category': self.o.category,
            'amount': formatters.amount(self.o.amount),
            'currency': self.currency,
            'note': self.o.note,
            'attachment': self.o.attachment,
            'deleted': bool(self.o.deleted),
        }
