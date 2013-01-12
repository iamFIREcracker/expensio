#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import groupby
from operator import attrgetter

import app.formatters as formatters
from app.models import Expense
from app.utils import protected
from app.utils import jsonify
from app.utils import parsedateparams
from app.utils import BaseHandler
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


class CategoriesHandler(BaseHandler):

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
                .filter(Expense.category.in_((e.category for e in updated)))
                .order_by(Expense.category.asc())
                .all())

        # Finally aggretate the amounts and the last modified date
        categories = [ComputeCategoryAggregate(group)
                        for (key, group) in groupby(
                            expenses, key=attrgetter('category'))]

        return jsonify(
                categories=[CategoryWrapper(c, self.current_user().currency)
                        for c in categories])
