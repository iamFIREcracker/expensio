#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime

import celery
import web

import app.formatters as formatters
import app.parsers as parsers
import app.tasks as tasks
from app.forms import expenses_add
from app.forms import expenses_edit
from app.forms import expenses_export
from app.forms import expenses_import
from app.managers import Categories
from app.models import Expense
from app.serializers import ExpenseSerializer
from app.upload import UploadedFile
from app.utils import active
from app.utils import owner
from app.utils import protected
from app.utils import jsonify
from app.utils import parsedateparams
from app.utils import BaseHandler



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
                expenses=[ExpenseSerializer(e, self.current_user().currency)
                        for e in expenses])


class ExpensesAddHandler(BaseHandler):
    @protected
    def GET(self):
        form = expenses_add()
        return web.ctx.render.expenses_add(expenses_add=form)

    @protected
    def POST(self):
        attachment = UploadedFile('attachment')
        form = expenses_add()

        if not form.validates():
            return jsonify(success=False,
                    errors=dict((i.name, i.note) for i in form.inputs
                        if i.note is not None))
        else:
            url = (os.path.join(web.ctx.home, web.ctx.uploadman.add(attachment))
                    if attachment else None)

            e = Expense(user_id=self.current_user().id,
                    amount=parsers.amount(form.d.amount),
                    category=form.d.category, note=form.d.note,
                    date=parsers.date_us(form.d.date), attachment=url)
            web.ctx.orm.add(e)
            web.ctx.orm.commit()
            e = web.ctx.orm.merge(e)

            if not Categories.exists(e.category, self.current_user().id):
                web.ctx.orm.add(
                        Categories.new(e.category, self.current_user().id))
                web.ctx.orm.commit()

            return jsonify(success=True,
                    expense=ExpenseSerializer(e, self.current_user().currency))


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
        return web.ctx.render.expenses_edit(expenses_edit=form)

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
            url = (os.path.join(web.ctx.home, web.ctx.uploadman.add(attachment))
                    if attachment else None)

            e = self.current_item()

            # Add a new expense being the copy of the current expense before
            # the edit operations have been applied
            deleted = Expense(original_id=e.id, user_id=self.current_user().id,
                    amount=e.amount, category=e.category, note=e.note,
                    date=e.date, deleted=True, attachment=e.attachment,
                    created=e.created)

            # Now apply edit operations on the current expense
            e.amount = parsers.amount(form.d.amount)
            e.category = form.d.category
            e.note = form.d.note
            e.date = parsers.date_us(form.d.date)
            if attachment:
                e.attachment = url
            # Touch the creation date not to break the algo used to return
            # categories sorted by the first time they were used
            e.created = datetime.now()

            # Bulk add
            web.ctx.orm.add_all([deleted, e])
            web.ctx.orm.commit()
            e = web.ctx.orm.merge(e)

            # Add the associated category if not already present
            if not Categories.exists(e.category, self.current_user().id):
                web.ctx.orm.add(
                        Categories.new(e.category, self.current_user().id))
                web.ctx.orm.commit()

            return jsonify(success=True,
                    expense=ExpenseSerializer(e, self.current_user().currency))


class ExpensesDeleteHandler(BaseHandler):
    @protected
    @owner(Expense)
    @active
    def GET(self, id):
        return web.ctx.render.expenses_delete(expense=self.current_item())

    @protected
    @owner(Expense)
    @active
    def POST(self, id):
        e = self.current_item()
        e.deleted = True
        web.ctx.orm.add(e)
        web.ctx.orm.commit()
        e = web.ctx.orm.merge(e)

        return jsonify(success=True,
                expense=ExpenseSerializer(e, self.current_user().currency))


class ExpensesImportHandler(BaseHandler):
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
            web.ctx.orm.commit()
            expenses = [web.ctx.orm.merge(e) for e in expenses]

            return jsonify(success=True,
                    expenses=[ExpenseSerializer(e, self.current_user().currency)
                            for e in expenses])


class ExpensesExportHandler(BaseHandler):
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
