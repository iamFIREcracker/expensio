#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import web

import app.formatters as formatters
import app.parsers as parsers
from app.forms import recurrences_add
#from app.forms import recurrences_edit
from app.models import Recurrence
from app.upload import UploadedFile
from app.utils import active
from app.utils import owner
from app.utils import protected
from app.utils import jsonify
from app.utils import BaseHandler



class RecurrenceWrapper(object):
    __serializable__ = {
            'id': lambda o: o.r.id,
            'created': lambda o: formatters.datetime(o.r.created),
            'updated': lambda o: formatters.datetime(o.r.updated),
            'yearly': lambda o: formatters.yearday(o.r.yearly),
            'monthly': lambda o: formatters.monthday(o.r.monthly),
            'weekly': lambda o: o.r.weekly,
            'category': lambda o: o.r.category,
            'amount': lambda o: formatters.amount(o.r.amount),
            'currency': lambda o: o.currency,
            'note': lambda o: o.r.note,
            'deleted': lambda o: bool(o.r.deleted),
            }

    def __init__(self, recurrence, currency):
        self.r = recurrence
        self.currency = currency


def RecurrencesInBetween(user_id, since, to):
    """
    Get all the recurrences associated to the given user, which have been created
    between `since` and `to`
    """
    return (web.ctx.orm.query(Recurrence)
                .filter_by(user_id=user_id)
                .filter(Recurrence.date >= since)
                .filter(Recurrence.date <= to))


def LatestRecurrencesInBetween(user_id, since, to, latest):
    """
    Get all the recurrences associated to the given user, which have been created
    between `since` and `to` and that have been modified after `latest`
    """
    return (RecurrencesInBetween(user_id, since, to)
                .filter(Recurrence.updated > latest))


class RecurrencesHandler(BaseHandler):
    @protected
    def GET(self):
        recurrences = (web.ctx.orm.query(Recurrence)
                .filter_by(user_id=self.current_user().id)
                .filter(Recurrence.deleted == False)
                .order_by(Recurrence.created.desc())
                .all())

        return jsonify(
                recurrences=[RecurrenceWrapper(e, self.current_user().currency)
                        for e in recurrences])


class RecurrencesAddHandler(BaseHandler):
    @protected
    def GET(self):
        form = recurrences_add()
        return web.ctx.render.recurrences_add(recurrences_add=form)

    @protected
    def POST(self):
        form = recurrences_add()

        if not form.validates():
            return jsonify(success=False,
                    reason=form.note,
                    errors=dict((i.name, i.note) for i in form.inputs
                        if i.note is not None))
        else:
            r = Recurrence(user_id=self.current_user().id,
                    yearly=parsers.yearday(form.d.yearly),
                    monthly=parsers.monthday(form.d.monthly),
                    weekly=parsers.weekday(form.d.weekly),
                    category=form.d.category, note=form.d.note,
                    amount=parsers.amount(form.d.amount))
            web.ctx.orm.add(r)
            r = web.ctx.orm.merge(r)

            return jsonify(success=True,
                    recurrence=RecurrenceWrapper(r, self.current_user().currency))


class RecurrencesEditHandler(BaseHandler):
    @protected
    @owner(Recurrence)
    @active
    def GET(self, id):
        form = recurrences_edit()
        item = self.current_item()
        form.fill(id=item.id, amount=formatters.amount(item.amount),
                category=item.category, note=item.note,
                date=formatters.date_us(item.date),
                oldattachment=item.attachment)
        return web.ctx.render.recurrences_edit(recurrences_edit=form)

    @protected
    @owner(Recurrence)
    @active
    def POST(self, id):
        attachment = UploadedFile('attachment')
        form = recurrences_edit()

        if not form.validates():
            return jsonify(success=False,
                    errors=dict((i.name, i.note) for i in form.inputs
                        if i.note is not None))
        else:
            url = (os.path.join(web.ctx.home, web.ctx.uploadman.add(attachment))
                    if attachment else None)

            e = self.current_item()

            # Add a new recurrence being the copy of the current recurrence before
            # the edit operations have been applied
            deleted = Recurrence(original_id=e.id, user_id=self.current_user().id,
                    amount=e.amount, category=e.category, note=e.note,
                    date=e.date, deleted=True, attachment=e.attachment)

            # Now apply edit operations on the current recurrence
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
                    recurrence=RecurrenceWrapper(e, self.current_user().currency))


class RecurrencesDeleteHandler(BaseHandler):
    @protected
    @owner(Recurrence)
    @active
    def GET(self, id):
        return web.ctx.render.recurrences_delete(recurrence=self.current_item())

    @protected
    @owner(Recurrence)
    @active
    def POST(self, id):
        e = self.current_item()
        e.deleted = True
        web.ctx.orm.add(e)
        e = web.ctx.orm.merge(e)

        return jsonify(success=True,
                recurrence=RecurrenceWrapper(e, self.current_user().currency))
