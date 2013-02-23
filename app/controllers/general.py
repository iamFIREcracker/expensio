#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

import web

import app.formatters as formatters
import app.parsers as parsers
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


class LogoutHandler():
    def GET(self):
        logout()
        raise web.found('/')


class WeekHandler(BaseHandler):
    @protected
    def GET(self):
        today = datetime.today()
        year = today.year
        month = today.month
        return web.ctx.render.thirthy_days(user=self.current_user(),
                                           year=year, month=month, ndays=7)


class ThirthyDaysHandler(BaseHandler):
    @protected
    def GET(self):
        today = datetime.today()
        year = today.year
        month = today.month
        return web.ctx.render.thirthy_days(user=self.current_user(),
                                           year=year, month=month, ndays=30)


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
