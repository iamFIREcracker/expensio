#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from itertools import groupby

import web
from sqlalchemy.sql import extract

from config import LATEST_DAYS_DATE_FORMAT
from expenses import ExpensesInBetween
from expenses import LatestExpensesInBetween
from formatters import dateformatter
from models import Expense
from utils import applicationinitializer
from utils import parsedateparams
from utils import protected
from utils import jsonify
from utils import BaseHandler



urls = (
    '/days.json', 'DaysHandler',
)


application = web.application(urls, globals())
applicationinitializer(application)


class DayWrapper(object):
    __serializable__ = {
            'date': lambda o: dateformatter(o.d[0], LATEST_DAYS_DATE_FORMAT),
            'updated': lambda o: dateformatter(o.d[1]),
            'amount': lambda o: o.d[2],
            'delta': lambda o: int(o.d[3]),
            'currency': lambda o: o.currency,
            }

    def __init__(self, day, currency):
        self.d = day
        self.currency = currency


def AccumulateDayAggregate(today):
    """
    Factory of functions to be used to compute per-day aggregation
    """
    def inner((date, amount, updated, delta), expense):
        """
        Function to be used together with `reduce` to compute aggregate
        information of a `day` object (i.e. date, amount per day, last modified
        date and time difference in respect of today).

        The function returns a inner function
        """
        return (
                expense.date,
                amount + expense.amount if not expense.deleted else amount,
                expense.updated if updated is None or expense.updated > updated
                        else updated,
                (expense.date.date() - today.date()).days)
    return inner


def ComputeDayAggregate(expenses):
    """
    Iterate all the expenses and compute, for each day, how much have been
    spent, when is the last time a new expense has been created for a certain
    day, and what is the time delta (in days) between the day under process and
    today.
    """
    today = datetime.today()
    (name, amount, updated, delta) = reduce(
            AccumulateDayAggregate(today), expenses, (None, 0, None, -99999))
    return name, updated, amount, delta


def PlainDate(expense):
    """
    Get the day in which the expense has been created (info regarding time is
    not taken into consideration).
    """
    return dateformatter(expense.date, LATEST_DAYS_DATE_FORMAT)


class DaysHandler(BaseHandler):
    @protected
    def GET(self):
        since, to, latest = parsedateparams()

        # Find all the expenses changed after `latest` and created between
        # `since` and `to`
        updated = (
                LatestExpensesInBetween(
                    self.current_user().id, since, to, latest)
                .order_by(Expense.date.asc())
                .all())

        # Of theses, extract all the 
        expenses = [] if not updated else (
                ExpensesInBetween(self.current_user().id, since, to)
                .filter(extract('year', Expense.date)
                    .in_(e.date.year for e in updated))
                .filter(extract('month', Expense.date)
                    .in_(e.date.month for e in updated))
                .filter(extract('day', Expense.date)
                    .in_(e.date.day for e in updated))
                .order_by(Expense.date.asc())
                .all())

        days = [ComputeDayAggregate(group)
                    for (key, group) in groupby(
                        expenses, key=PlainDate)]

        d = jsonify(
                days=[DayWrapper(d, self.current_user().currency)
                    for d in days])
        web.debug(d)
        return d


if __name__ == '__main__':
    application.run()
