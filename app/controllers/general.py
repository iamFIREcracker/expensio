#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import datetime

import web

import app.formatters as formatters
import app.parsers as parsers
from app.utils import BaseHandler
from app.forms import expenses_add

class MainHandler(BaseHandler):
    def GET(self, year=None, month=None):
        if not self.current_user():
            return web.ctx.render.info()
        else:
            # Validate `year` and `month`, if specified
            today = datetime.today()
            year = year if year is not None else today.year
            month = month if month is not None else today.month
            parsers.period(formatters.period(datetime(year, month, 1)))

            form = expenses_add()

            return web.ctx.render.index(user=self.current_user(),
                                        year=year, month=month,
                                        expenses_add=form)


class LogoutHandler():
    def GET(self):
        web.setcookie('user', '', expires=time.time() - 86400)
        web.seeother('/')
