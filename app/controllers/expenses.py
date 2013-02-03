#!/usr/bin/env python
# -*- coding: utf-8 -*-

import celery
import web

import app.formatters as formatters
import app.parsers as parsers
import app.tasks as tasks
from app.forms import expenses_add
from app.forms import expenses_edit
from app.forms import expenses_export
from app.forms import expenses_import
from app.models import Expense
from app.upload import UploadedFile
from app.utils import active
from app.utils import owner
from app.utils import protected
from app.utils import jsonify
from app.utils import parsedateparams
from app.utils import BaseHandler



class ExpenseWrapper(object):
    __serializable__ = {
            'id': lambda o: o.e.id,
            'date': lambda o: formatters.date(o.e.date),
            'created': lambda o: formatters.datetime(o.e.created),
            'updated': lambda o: formatters.datetime(o.e.updated),
            'category': lambda o: o.e.category,
            'amount': lambda o: formatters.amount(o.e.amount),
            'currency': lambda o: o.currency,
            'note': lambda o: o.e.note,
            'attachment': lambda o: o.e.attachment,
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
        attachment = UploadedFile('attachment')
        form = expenses_add()

        if not form.validates():
            return jsonify(success=False,
                    errors=dict((i.name, i.note) for i in form.inputs
                        if i.note is not None))
        else:
            url = web.ctx.uploadman.add(attachment) if attachment else None

            e = Expense(user_id=self.current_user().id,
                    amount=parsers.amount(form.d.amount),
                    category=form.d.category, note=form.d.note,
                    date=parsers.date_us(form.d.date), attachment=url)
            web.ctx.orm.add(e)
            e = web.ctx.orm.merge(e)

            return jsonify(success=True,
                    expense=ExpenseWrapper(e, self.current_user().currency))


class ExpensesEditHandler(BaseHandler):
    @protected
    @owner(Expense)
    @active
    def GET(self, id):
        form = expenses_edit()
        item = self.current_item()
        form.fill(id=item.id, amount=formatters.amount(item.amount),
                category=item.category, note=item.note,
                date=formatters.date_us(item.date),
                oldattachment=item.attachment)
        return web.ctx.render.expenses_edit_complete(user=self.current_user(),
                expenses_edit=form)

    @protected
    @owner(Expense)
    @active
    def POST(self, id):
        attachment = UploadedFile('attachment')
        form = expenses_edit()

        if not form.validates():
            return jsonify(success=False,
                    errors=dict((i.name, i.note) for i in form.inputs
                        if i.note is not None))
        else:
            url = web.ctx.uploadman.add(attachment) if attachment else None

            e = self.current_item()

            # Add a new expense being the copy of the current expense before
            # the edit operations have been applied
            deleted = Expense(original_id=e.id, user_id=self.current_user().id,
                    amount=e.amount, category=e.category, note=e.note,
                    date=e.date, deleted=True, attachment=e.attachment)

            # Now apply edit operations on the current expense
            e.amount = parsers.amount(form.d.amount)
            e.category = form.d.category
            e.note = form.d.note
            e.date = parsers.date_us(form.d.date)
            if attachment:
                e.attachment = url

            # Bulk add
            web.ctx.orm.add_all([deleted, e])
            e = web.ctx.orm.merge(e)

            return jsonify(success=True,
                    expense=ExpenseWrapper(e, self.current_user().currency))


class ExpensesDeleteHandler(BaseHandler):
    @protected
    @owner(Expense)
    @active
    def POST(self, id):
        e = self.current_item()
        e.deleted = True
        web.ctx.orm.add(e)
        e = web.ctx.orm.merge(e)

        return jsonify(success=True,
                expense=ExpenseWrapper(e, self.current_user().currency))


class ExpensesImportHandler(BaseHandler):
    @protected
    def GET(self):
        return web.ctx.render.expenses_import_complete(user=self.current_user(),
                expenses_import=expenses_import())

    @protected
    def POST(self):
        form = expenses_import()
        if not form.validates():
            return jsonify(success=False,
                    errors=dict((i.name, i.note) for i in form.inputs
                        if i.note is not None))
        else:
            expenses = [Expense(user_id=self.current_user().id, date=date,
                        category=category, amount=amount, note=note)
                    for (date, category, amount, note)
                            in parsers.expenses(form.d.data)]
            web.ctx.orm.add_all(expenses)
            expenses = [web.ctx.orm.merge(e) for e in expenses]

            return jsonify(success=True,
                    expenses=[ExpenseWrapper(e, self.current_user().currency)
                            for e in expenses])


class ExpensesExportHandler(BaseHandler):

    @protected
    def GET(self):
        return web.ctx.render.expenses_export_complete(user=self.current_user(),
                expenses_export=expenses_export())

    @protected
    def POST(self):
        form = expenses_export()
        if not form.validates():
            return jsonify(success=False,
                    errors=dict((i.name, i.note) for i in form.inputs
                        if i.note is not None))
        else:
            task_id = tasks.ExpensesExportTSVTask.delay(
                    web.ctx.exportman, self.current_user()).task_id
            return jsonify(success=True,
                    goto='/expenses/export/tsv/status/%s' % task_id)


class ExpensesExportTSVStatusHandler(BaseHandler):

    @protected
    def GET(self, task_id):
        try:
            retval = (tasks.ExpensesExportTSVTask.AsyncResult(task_id)
                    .get(timeout=1.0))
        except celery.exceptions.TimeoutError:
            return jsonify(success=False, goto=web.ctx.path)
        else:
            return jsonify(success=True, goto=retval)
