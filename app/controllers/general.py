#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import web

from app.utils import BaseHandler
from app.forms import expenses_add

class MainHandler(BaseHandler):
    def GET(self):
        if not self.current_user():
            return web.ctx.render.info()
        else:
            form = expenses_add()

            return web.ctx.render.index(user=self.current_user(),
                    expenses_add=form)


class LogoutHandler():
    def GET(self):
        web.setcookie('user', '', expires=time.time() - 86400)
        web.seeother('/')
