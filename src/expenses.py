#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

import web

from formatters import dateformatter
from forms import expenses_add
from forms import expenses_edit
from forms import expenses_import
from forms import FORM_DATE_FORMAT
from forms import FORM_PERIOD_FORMAT
from models import Expense
from utils import applicationinitializer
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
            'date': lambda o: dateformatter(o.e.date),
            'created': lambda o: dateformatter(o.e.created),
            'updated': lambda o: dateformatter(o.e.updated),
            'category': lambda o: o.e.category,
            'amount': lambda o: o.e.amount,
            'currency': lambda o: o.currency,
            'note': lambda o: o.e.note,
            'deleted': lambda o: bool(o.e.deleted),
            }

    def __init__(self, expense, currency):
        self.e = expense
        self.currency = currency


def ExpensesInBetween(user_id, since, to, latest):
    """
    Get all the expenses associated to the given user, which have been created
    between `since` and `to` and that have been modified after `latest`
    """
    return (web.ctx.orm.query(Expense)
                .filter_by(user_id=user_id)
                .filter(Expense.date >= since)
                .filter(Expense.date < to)
                .filter(Expense.updated > latest))


class ExpensesHandler(BaseHandler):
    @protected
    def GET(self):
        since, to, latest = parsedateparams()

        expenses = (
                ExpensesInBetween(self.current_user().id, since, to, latest)
                .order_by(Expense.date.asc())
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
                    note=form.d.note,
                    date=datetime.strptime(form.d.date, FORM_DATE_FORMAT))
            web.ctx.orm.add(e)
        return web.ctx.render.expenses_add(expenses_add=form)


class ExpensesEditHandler(BaseHandler):
    @protected
    @owner(Expense)
    def GET(self, id):
        form = expenses_edit()
        item = self.current_item()
        form.fill(id=item.id, amount=item.amount, category=item.category,
                note=item.note,
                date=datetime.strftime(item.date, FORM_DATE_FORMAT))
        return web.ctx.render.expenses_edit_complete(expenses_edit=form)

    @protected
    @owner(Expense)
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
            e.date = datetime.strptime(form.d.date, FORM_DATE_FORMAT)
            web.ctx.orm.add(e)
        return web.ctx.render.expenses_edit(expenses_edit=form)


class ExpensesDeleteHandler(BaseHandler):
    @protected
    @owner(Expense)
    def POST(self, id):
        e = self.current_item()
        e.deleted = True
        web.ctx.orm.add(e)

        form = expenses_edit()
        return web.ctx.render.expenses_edit(expenses_edit=form)


class ExpensesImportHandler(BaseHandler):
    @protected
    def GET(self):
        return web.ctx.render.expenses_import(user=self.current_user(),
                form=expenses_import())

    @protected
    def POST(self):
        form = expenses_import()
        if not form.validates():
            return web.ctx.render.expenses_import(
                    user=self.current_user(), form=form)

        for line in form.d.expenses.split('\r\n'):
            tokens = line.split('\t')
            date = datetime.strptime(form.d.period + tokens[0],
                    FORM_PERIOD_FORMAT + '%d')
            amount = tokens[2].split()[1]
            note = tokens[3] if len(tokens) >= 4 else ''
            expense = Expense(user_id=self.current_user().id, date=date,
                    category=tokens[1], amount=amount, note=note)
            web.ctx.orm.add(expense)
        web.seeother('/')


if __name__ == '__main__':
    application.run()
