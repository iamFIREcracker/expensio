#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

import web

import formatters
import parsers
from forms import expenses_add
from forms import expenses_edit
from forms import expenses_import
from forms import fetch_expenses
from forms import FORM_DATE_FORMAT
from models import Expense
from utils import applicationinitializer
from utils import active
from utils import owner
from utils import protected
from utils import jsonify
from utils import parsedateparams
from utils import BaseHandler



urls = (
    '/expenses.json', 'ExpensesHandler',
    '/expenses/add', 'ExpensesAddHandler',
    '/expenses/(.+)/edit', 'ExpensesEditHandler',
    '/expenses/(.+)/delete', 'ExpensesDeleteHandler',
    '/expenses/import', 'ExpensesImportHandler',
)


application = web.application(urls, globals())
applicationinitializer(application)


class ExpenseWrapper(object):
    __serializable__ = {
            'id': lambda o: o.e.id,
            'date': lambda o: formatters.date(o.e.date),
            'created': lambda o: formatters.datetime(o.e.created),
            'updated': lambda o: formatters.datetime(o.e.updated),
            'category': lambda o: o.e.category,
            'amount': lambda o: o.e.amount,
            'currency': lambda o: o.currency,
            'note': lambda o: o.e.note,
            'deleted': lambda o: bool(o.e.deleted),
            }

    def __init__(self, expense, currency):
        self.e = expense
        self.currency = currency


def ExpensesInBetween(user_id, since, to):
    """
    Get all the expenses associated to the given user, which have been created
    between `since` and `to`
    """
    return (web.ctx.orm.query(Expense)
                .filter_by(user_id=user_id)
                .filter(Expense.date >= since)
                .filter(Expense.date <= to))


def LatestExpensesInBetween(user_id, since, to, latest):
    """
    Get all the expenses associated to the given user, which have been created
    between `since` and `to` and that have been modified after `latest`
    """
    return (ExpensesInBetween(user_id, since, to)
                .filter(Expense.updated > latest))


class ExpensesHandler(BaseHandler):
    @protected
    def GET(self):
        since, to, latest = parsedateparams()

        expenses = (
                LatestExpensesInBetween(
                    self.current_user().id, since, to, latest)
                .order_by(Expense.date.desc())
                .all())

        return jsonify(
                expenses=[ExpenseWrapper(e, self.current_user().currency)
                        for e in expenses])


class ExpensesAddHandler(BaseHandler):
    @protected
    def POST(self):
        form = expenses_add()
        if form.validates():
            e = Expense(user_id=self.current_user().id,
                    amount=float(form.d.amount), category=form.d.category,
                    note=form.d.note, date=parsers.date(form.d.date))
            web.ctx.orm.add(e)
        return web.ctx.render.expenses_add(expenses_add=form)


class ExpensesEditHandler(BaseHandler):
    @protected
    @owner(Expense)
    @active
    def GET(self, id):
        form = expenses_edit()
        item = self.current_item()
        form.fill(id=item.id, amount=item.amount, category=item.category,
                note=item.note, date=parsers.date(item.date))
        return web.ctx.render.expenses_edit_complete(expenses_edit=form)

    @protected
    @owner(Expense)
    @active
    def POST(self, id):
        form = expenses_edit()
        if form.validates():
            e = self.current_item()

            # Add a new expense being the copy of the current expense before
            # the edit operations have been applied
            deleted = Expense(original_id=e.id, user_id=self.current_user().id,
                    amount=e.amount, category=e.category, note=e.note,
                    date=e.date, deleted=True)
            web.ctx.orm.add(deleted)

            # Now apply edit operations on the current expense
            e.amount = float(form.d.amount)
            e.category = form.d.category
            e.note = form.d.note
            e.date = parsers.date(form.d.date)
            web.ctx.orm.add(e)
        return web.ctx.render.expenses_edit(expenses_edit=form)


class ExpensesDeleteHandler(BaseHandler):
    @protected
    @owner(Expense)
    @active
    def POST(self, id):
        e = self.current_item()
        e.deleted = True
        web.ctx.orm.add(e)

        form = expenses_edit()
        return web.ctx.render.expenses_edit(expenses_edit=form)


class ExpensesImportHandler(BaseHandler):
    @protected
    def GET(self):
        return web.ctx.render.expenses_import_complete(user=self.current_user(),
                expenses_import=expenses_import())

    @protected
    def POST(self):
        form = expenses_import()
        if form.validates():
            web.ctx.orm.add_all(
                Expense(user_id=self.current_user().id, date=date,
                        category=category, amount=amount, note=note)
                    for (date, category, amount, note)
                            in fetch_expenses(form.d))
        return web.ctx.render.expenses_import(
                user=self.current_user(), expenses_import=form)


if __name__ == '__main__':
    application.run()
