#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import web

from . import models
from . import sessions
from auth import LoginGoogleHandler
from auth import LoginGoogleAuthorizedHandler
from auth import LoginFacebookHandler
from auth import LoginFacebookAuthorizedHandler
from auth import LoginTwitterHandler
from auth import LoginTwitterAuthorizedHandler
from auth import LoginFakeHandler
from auth import LoginFakeAuthorizedHandler
from categories import CategoriesHandler
from days import DaysHandler
from expenses import ExpensesHandler
from expenses import ExpensesAddHandler
from expenses import ExpensesEditHandler
from expenses import ExpensesDeleteHandler
from expenses import ExpensesImportHandler
from users import UsersEditHandler
from forms import expenses_add
from utils import applicationinitializer
from utils import BaseHandler


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



urls = (
    '/', MainHandler,

    '/login/google', LoginGoogleHandler,
    '/login/google/authorized', LoginGoogleAuthorizedHandler,
    '/login/facebook', LoginFacebookHandler,
    '/login/facebook/authorized', LoginFacebookAuthorizedHandler,
    '/login/twitter', LoginTwitterHandler,
    '/login/twitter/authorized', LoginTwitterAuthorizedHandler,
    '/login/fake', LoginFakeHandler,
    '/login/fake/authorized', LoginFakeAuthorizedHandler,
    '/logout', LogoutHandler,

    '/users/(.+)/edit', UsersEditHandler,

    '/days.json', DaysHandler,

    '/categories.json', CategoriesHandler,

    '/expenses.json', ExpensesHandler,
    '/expenses/add', ExpensesAddHandler,
    '/expenses/(.+)/edit', ExpensesEditHandler,
    '/expenses/(.+)/delete', ExpensesDeleteHandler,
    '/expenses/import', ExpensesImportHandler,
)



app = web.application(urls, globals())
applicationinitializer(app)
app = app.wsgifunc()
