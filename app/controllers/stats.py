#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

from itertools import groupby
from operator import attrgetter

import web

import app.config as config
import app.formatters as formatters
from app.models import Expense
from app.utils import jsonify
from app.utils import parsedateparams
from app.utils import protected
from app.utils import BaseHandler
from app.query import Expenses
from .expenses import LatestExpensesInBetween
from .expenses import ExpensesInBetween



class CategoryWrapper(object):
    __serializable__ = {
        'name': lambda o: o.c[0],
        'updated': lambda o: formatters.datetime(o.c[1]),
        'amount': lambda o: formatters.amount(o.c[2]),
        'currency': lambda o: o.currency,
        }

    def __init__(self, category, currency):
        self.c = category
        self.currency = currency


def AccumulateCategoryAggregate((name, amount, updated), expense):
    """
    Function to be used in conjunction with `reduce` in order to extract the
    name, the amount and when a certain category was last touched, given
    a sequence of expenses.

    Note:  the function expects a sequence of expenses tagged with the same
    category.
    """
    return (
            expense.category,
            amount + expense.amount if not expense.deleted else amount,
            expense.updated if updated is None or expense.updated > updated
                    else updated)


def ComputeCategoryAggregate(expenses):
    """
    Iterate all the input expenses in order to compute, for each category, an
    aggregate of how much have been spent for each category, and what is the
    last time a new expense for a certain category has been done.
    """
    (name, amount, updated) = reduce(
            AccumulateCategoryAggregate, expenses, (None, 0, None))
    return name, updated, amount


class StatsCategoriesHandler(BaseHandler):

    @protected
    def GET(self):
        since, to, latest = parsedateparams()

        # Find all the expenses which have been *created* in between `since` and
        # `to` and *modified* after `latest`.
        updated = (
                LatestExpensesInBetween(
                    self.current_user().id, since, to, latest)
                .order_by(Expense.category.asc())
                .all())

        # Of these, extract the categories and look for all the expenses
        # between `since` and `to` having one of the extracted categories.
        expenses = [] if not updated else (
                ExpensesInBetween(self.current_user().id, since, to)
                .filter(Expense.category.in_(set(e.category for e in updated)))
                .order_by(Expense.category.asc())
                .all())

        # Finally aggretate the amounts and the last modified date
        categories = [ComputeCategoryAggregate(group)
                        for (key, group) in groupby(
                            expenses, key=attrgetter('category'))]

        return jsonify(
                stats=dict(
                    categories=[CategoryWrapper(c, self.current_user().currency)
                        for c in categories]))


class DayWrapper(object):
    __serializable__ = {
            'date': lambda o: formatters.date(o.d[0]),
            'updated': lambda o: formatters.datetime(o.d[1]),
            'income': lambda o: formatters.amount(o.d[2]),
            'outcome': lambda o: formatters.amount(o.d[3]),
            'delta': lambda o: int(o.d[4]),
            'currency': lambda o: o.currency,
            }

    def __init__(self, day, currency):
        self.d = day
        self.currency = currency


def AccumulateDayAggregate((date, income, outcome, updated), expense):
    """
    Function to be used together with `reduce` to compute aggregate
    information of a `day` object (i.e. date, amount per day, last modified
    date and time difference in respect of today).

    The function returns a inner function
    """
    return (
            expense.date,
            income + expense.amount if expense.amount < 0 else -income,
            outcome + expense.amount if expense.amount > 0 else outcome,
            expense.updated if updated is None or expense.updated > updated
                    else updated)


def ComputeDayAggregate(delta, expenses):
    """
    Iterate all the expenses and compute, for each day, how much have been
    spent, when is the last time a new expense has been created for a certain
    day, and what is the time delta (in days) between the day under process and
    today.
    """
    (name, income, outcome, updated) = reduce(
            AccumulateDayAggregate,
            filter(lambda e: not e.deleted, expenses),
            (None, 0, 0, None))
    return name, updated, income, outcome, delta


def days_since(reference):
    """Return a function returning the difference in days between `reference`
    and another possible date."""
    def inner(current):
        return (reference.date() - current.date()).days
    return inner


class StatsDaysHandler(BaseHandler):
    @protected
    def GET(self):
        since, to, _ = parsedateparams()
        sincenewest = days_since(to)
        bins = int(web.input(bins=config.DEFAULT_STATS_BINS).bins)

        expenses = (
                Expenses()
                    .mine(self.current_user().id)
                    .active()
                    .in_between(since, to)
                    .ordered_by(Expense.date.asc())
                    .all())

        deltas = sincenewest(expenses[0].date) + 1 # Take `to` into account
        expensesperbean = deltas / bins

        days = [ComputeDayAggregate(key, group)
                   for key, group in groupby(expenses,
                           key=lambda e: -(sincenewest(e.date) // expensesperbean))]

        return jsonify(
                stats=dict(
                    days=[DayWrapper(d, self.current_user().currency)
                        for d in days]))
