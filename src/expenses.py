#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

import web
from sqlalchemy import extract
from sqlalchemy import func

from config import DATE_FORMAT
from config import EPOCH
from formatters import dateformatter
from forms import expenses_add
from forms import expenses_edit
from forms import expenses_import
from forms import FORM_DATE_FORMAT
from forms import FORM_PERIOD_FORMAT
from handlers import owner
from handlers import protected
from handlers import BaseHandler
from models import Expense
from utils import jsonify


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


class CategoryWrapper(object):
    __serializable__ = {
        'name': lambda o: o.c[0],
        'amount': lambda o: o.c[1],
        'currency': lambda o: o.currency,
        }

    def __init__(self, category, currency):
        self.c = category
        self.currency = currency


class ExpensesHandler(BaseHandler):
    @protected
    def GET(self):
        today = datetime.today()
        data = web.input(year=today.year, month=today.month,
                latest=EPOCH)
        user_id = self.current_user().id

        year = int(data.year)
        month = int(data.month)
        latest = datetime.strptime(
                data.latest if data.latest else EPOCH, DATE_FORMAT)

        expenses = (web.ctx.orm.query(Expense)
                .filter_by(user_id=user_id)
                .filter(extract('year', Expense.date) == year)
                .filter(extract('month', Expense.date) == month)
                .filter(Expense.updated > latest)
                .order_by(Expense.date.desc())
                .all())

        categories = [] if not expenses else (
                web.ctx.orm.query(Expense.category, func.sum(Expense.amount))
                    .filter_by(user_id=user_id)
                    .filter(extract('year', Expense.date) == year)
                    .filter(extract('month', Expense.date) == month)
                    .filter(Expense.category.in_((e.category for e in expenses)))
                    .order_by(Expense.category)
                    .group_by(Expense.category)
                    .all())

        return jsonify(
                expenses=[ExpenseWrapper(e, self.current_user().currency) for e in expenses],
                categories=[CategoryWrapper(c, self.current_user().currency) for c in categories])


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
                note=item.note, date=datetime.strftime(item.date, FORM_DATE_FORMAT))
        return web.ctx.render.expenses_edit_complete(expenses_edit=form)

    @protected
    @owner(Expense)
    def POST(self, id):
        form = expenses_edit()
        if form.validates():
            # Delete old item
            old = self.current_item()
            old.amount = 0
            old.deleted = True
            web.ctx.orm.add(old)

            # Add new one
            e = Expense(user_id=self.current_user().id,
                    amount=float(form.d.amount), category=form.d.category,
                    note=form.d.note,
                    date=datetime.strptime(form.d.date, FORM_DATE_FORMAT))
            web.ctx.orm.add(e)
        return web.ctx.render.expenses_edit(expenses_edit=form)


class ExpensesDeleteHandler(BaseHandler):
    @protected
    @owner(Expense)
    def POST(self, id):
        e = self.current_item()
        e.amount = 0
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
