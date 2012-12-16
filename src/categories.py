#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import groupby
from operator import attrgetter

from expenses import ExpensesInBetween
from formatters import dateformatter
from models import Expense
from utils import protected
from utils import jsonify
from utils import parsedateparams
from utils import BaseHandler


urls = (
    '/categories.json', 'CategoriesHandler',
)

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


def AccumulateAmountsAndLatestModified((amount, updated), expense):
    return (
            amount + expense.amount if not expense.deleted else amount,
            expense.updated if updated is None or expense.updated > updated
                    else updated)


def ComputeCategoryAggregate(name, expenses):
    (amount, updated) = reduce(
            AccumulateAmountsAndLatestModified, expenses, (0, None))
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
        categories = [ComputeCategoryAggregate(key, group)
                        for (key, group) in groupby(
                            expenses, key=attrgetter('category'))]

        return jsonify(
                categories=[CategoryWrapper(c, self.current_user().currency)
                        for c in categories])
