#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

import web

import app.formatters as formatters
import app.parsers as parsers
from app.forms import expenses_import
from app.forms import expenses_export
from app.forms import users_avatar
from app.forms import users_connect
from app.forms import users_edit
from app.forms import users_delete
from app.utils import logout
from app.utils import protected
from app.utils import BaseHandler
from app.forms import expenses_add



class MainHandler(BaseHandler):
    def GET(self, year=None, month=None):
        if not self.current_user():
            return web.ctx.render.info()
        else:
            # Validate `year` and `month`, if specified
            today = datetime.today()
            year = int(year) if year is not None else today.year
            month = int(month) if month is not None else today.month
            parsers.period(formatters.period(datetime(year, month, 1)))

            form = expenses_add()

            return web.ctx.render.index(user=self.current_user(),
                                        year=year, month=month,
                                        expenses_add=form)


class UsersProfileHandler(BaseHandler):
    @protected
    def GET(self):
        user = self.current_user()
        avatar = users_avatar()
        avatar.fill(id=user.id, avatar=user.avatar)
        connect = users_connect()
        connect.fill(google=(user.google_id is not None),
                     facebook=(user.facebook_id is not None),
                     twitter=(user.twitter_id is not None),
                     fake=(not any([user.google_id is not None,
                                    user.facebook_id is not None,
                                    user.twitter_id is not None])))
        edit = users_edit()
        edit.fill(id=user.id, name=user.name, currency=user.currency)
        return web.ctx.render.profile(user=self.current_user(),
                current='profile', users_avatar=avatar, users_connect=connect,
                users_edit=edit)


class UsersDeactivateHandler(BaseHandler):
    @protected
    def GET(self):
        form = users_delete()
        form.fill(id=self.current_user().id)
        return web.ctx.render.deactivate_complete(user=self.current_user(),
                current='deactivate', users_delete=form)


class LogoutHandler():
    def GET(self):
        logout()
        raise web.found('/')


class RecurringHandler(BaseHandler):
    @protected
    def GET(self):
        return web.ctx.render.recurring_complete(user=self.current_user(),
                current='recurring')


class ImportHandler(BaseHandler):
    @protected
    def GET(self):
        return web.ctx.render.expenses_import_complete(user=self.current_user(),
                current='import', expenses_import=expenses_import())


class ExportHandler(BaseHandler):
    @protected
    def GET(self):
        return web.ctx.render.expenses_export_complete(user=self.current_user(),
                current='export', expenses_export=expenses_export())


class StatsHandler(BaseHandler):
    days = {'quadrimester': 120, 'year': 365, 'life': 1000}

    @protected
    def GET(self, mode=None):
        today = datetime.today()
        year = today.year
        month = today.month
        return web.ctx.render.stats2(user=self.current_user(),
                                     year=year, month=month, current=mode,
                                     ndays=self.days[mode])
