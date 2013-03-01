#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web

from app.models import Expense


class Expenses(object):

    def __init__(self):
        self._q = web.ctx.orm.query(Expense)

    def active(self):
        """ Filter out all the `deleted` expenses """
        self._q = self._q.filter_by(deleted=False)
        return self

    def all(self):
        return self._q.all()

    def in_between(self, since, to):
        """ Include all the expenses with a date between `since` and `to` """
        self._q = (self._q
                .filter(Expense.date >= since)
                .filter(Expense.date <= to))
        return self

    def mine(self, user_id):
        """Filter out all the expenses not belonging to given `user_id`"""
        self._q = self._q.filter_by(user_id=user_id)
        return self

    def newer_than(self, latest):
        """Filter out all the expenses last touched before `latest`"""
        self._q = self._q.filter(Expense.updated > latest)
        return self

    def ordered_by(self, order):
        """Apply given order logic to the current query """
        self._q = self._q.order_by(order)
        return self
