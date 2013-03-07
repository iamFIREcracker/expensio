#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

from datetime import timedelta
from itertools import groupby
from math import ceil
from operator import attrgetter

import web

import app.formatters as formatters
import app.parsers as parsers
from app.models import Expense
from app.utils import jsonify
from app.utils import input_
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
        'income': lambda o: formatters.amount(o.c[2]),
        'outcome': lambda o: formatters.amount(o.c[3]),
        'currency': lambda o: o.currency,
        }

    def __init__(self, category, currency):
        self.c = category
        self.currency = currency


def AccumulateCategoryAggregate((name, income, outcome, updated), expense):
    """
    Function to be used in conjunction with `reduce` in order to extract the
    name, the amount and when a certain category was last touched, given
    a sequence of expenses.

    Note:  the function expects a sequence of expenses tagged with the same
    category.
    """
    return (
            expense.category,
            income + expense.amount if expense.amount < 0 else income,
            outcome + expense.amount if expense.amount > 0 else outcome,
            expense.updated if updated is None or expense.updated > updated
                    else updated)


def ComputeCategoryAggregate(expenses):
    """
    Iterate all the input expenses in order to compute, for each category, an
    aggregate of how much have been spent for each category, and what is the
    last time a new expense for a certain category has been done.
    """
    (name, income, outcome, updated) = reduce(
            AccumulateCategoryAggregate,
            filter(lambda e: not e.deleted, expenses),
            (None, 0, 0, None))
    return name, updated, income, outcome


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
            'date': lambda o: formatters.date(o.d['date']),
            'income': lambda o: formatters.amount(o.d['income']),
            'outcome': lambda o: formatters.amount(o.d['outcome']),
            'currency': lambda o: o.currency,
            }

    def __init__(self, day, currency):
        self.d = day
        self.currency = currency


def ComputeDayAggregate(seed, expenses):
    """
    Iterate all the expenses and compute, for each day, how much have been
    spent, when is the last time a new expense has been created for a certain
    day, and what is the time delta (in days) between the day under process and
    today.
    """
    def aggregate(aggregate, expense):
        aggregate['income'] += expense.amount if expense.amount < 0 else 0
        aggregate['outcome'] += expense.amount if expense.amount > 0 else 0
        return aggregate

    return reduce(aggregate, filter(lambda e: not e.deleted, expenses), seed)


def days_to(reference):
    """Return a function returning the difference in days between `reference`
    and another possible date.
    
    Example:
        days_to(TOM + 2)(TOD) =  3
        days_to(TOM)(TOD)     =  1 
        days_to(YES)(TOD)     = -1
    """
    def inner(current):
        return (reference.date() - current.date()).days
    return inner


def dates_for_bins(since, to, bins, daysperbean):
    """Generator returning all representative days for the bins of the given
    period.
    """
    for i in xrange(bins - 1, -1, -1):
        # ``daysperbean`` is not guaranteed to be an integer value, hence use
        # ``math.ceil`` to fill bins evenly
        yield to.date() - timedelta(days=ceil(i*daysperbean))


def groupby_bin(dates):
    """Function factory handy to group expenses into bin.
    
    Given the input array of dates, the returned function will traverse such
    array until the current expense date is smaller than the current array
    date."""
    it = iter(enumerate(dates))
    # Work around the fact that 2.X does not have the keyword ``nonlocal`` to
    # modify variables from outer scopes:  store the context into a container
    # which allows us to edit its elements, leaving the container itself as is
    mutable = {'cur': it.next()}
    def inner(expense):
        while mutable['cur']:
            key, date = mutable['cur']
            if expense.date.date() < date:
                return key
            mutable['cur'] = it.next()
    return inner


class StatsDaysHandler(BaseHandler):
    @protected
    def GET(self):
        d = input_(since=lambda v: parsers.date(v),
                   to=lambda v: parsers.date(v),
                   bins=lambda v: int(v))
        torightleg = days_to(d.to)
        if torightleg(d.since) < d.bins:
            # TODO add some log here
            raise web.badrequest()

        expenses = (
                Expenses()
                    .mine(self.current_user().id)
                    .active()
                    .in_between(d.since, d.to)
                    .ordered_by(Expense.date.asc())
                    .all())

        deltadays = torightleg(d.since) + 1 # Take right leg into account
        daysperbean = deltadays / d.bins

        dates = list(dates_for_bins(d.since, d.to, d.bins, daysperbean))
        days = [{ 'date': date, 'income': 0.0, 'outcome': 0.0 }
                    for date in dates]

        [ComputeDayAggregate(days[key], group)
                for key, group in groupby(expenses, key=groupby_bin(dates))]

        return jsonify(
                stats=dict(
                    days=[DayWrapper(d, self.current_user().currency)
                        for d in days]))
