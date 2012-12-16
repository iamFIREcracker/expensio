#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import groupby
from operator import attrgetter

import web

from expenses import ExpensesInBetween
from formatters import dateformatter
from models import Expense
from utils import applicationinitializer
from utils import protected
from utils import jsonify
from utils import parsedateparams
from utils import BaseHandler



urls = (
    '/categories.json', 'CategoriesHandler',
)

application = web.application(urls, globals())
applicationinitializer(application)

class CategoryWrapper(object):
    __serializable__ = {
        'name': lambda o: o.c[0],
        'updated': lambda o: dateformatter(o.c[1]),
        'amount': lambda o: o.c[2],
        'currency': lambda o: o.currency,
        }

    def __init__(self, category, currency):
        self.c = category
        self.currency = currency


def AccumulateAmountsAndLatestModified((name, amount, updated), expense):
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
            AccumulateAmountsAndLatestModified, expenses, (None, 0, None))
    return name, updated, amount


class CategoriesHandler(BaseHandler):

    @protected
    def GET(self):
        since, to, latest = parsedateparams()

        expenses = (
                ExpensesInBetween(self.current_user().id, since, to, latest)
                .group_by(Expense.category)
                .order_by(Expense.category.asc())
                .all())
        categories = [ComputeCategoryAggregate(group)
                        for (key, group) in groupby(
                            expenses, key=attrgetter('category'))]

        return jsonify(
                categories=[CategoryWrapper(c, self.current_user().currency)
                        for c in categories])


if __name__ == '__main__':
    application.run()
