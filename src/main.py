#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import unicode_literals

import time
from datetime import datetime

import web

from auth import LoginGoogleHandler
from auth import LoginGoogleAuthorizedHandler
from auth import LoginFacebookHandler
from auth import LoginFacebookAuthorizedHandler
from auth import LoginTwitterHandler
from auth import LoginTwitterAuthorizedHandler
from categories import CategoriesHandler
from days import DaysHandler
from expenses import ExpensesHandler
from expenses import ExpensesAddHandler
from expenses import ExpensesEditHandler
from expenses import ExpensesDeleteHandler
from expenses import ExpensesImportHandler
from users import UsersEditHandler
from forms import expenses_add
from forms import FORM_DATE_FORMAT
from utils import applicationinitializer
from utils import BaseHandler



urls = (
    '/', 'MainHandler',

    '/login/google', 'LoginGoogleHandler',
    '/login/google/authorized', 'LoginGoogleAuthorizedHandler',
    '/login/facebook', 'LoginFacebookHandler',
    '/login/facebook/authorized', 'LoginFacebookAuthorizedHandler',
    '/login/twitter', 'LoginTwitterHandler',
    '/login/twitter/authorized', 'LoginTwitterAuthorizedHandler',
    '/logout', 'LogoutHandler',

    '/users/(.+)/edit', 'UsersEditHandler',

    '/days.json', 'DaysHandler',

    '/categories.json', 'CategoriesHandler',

    '/expenses.json', 'ExpensesHandler',
    '/expenses/add', 'ExpensesAddHandler',
    '/expenses/(.+)/edit', 'ExpensesEditHandler',
    '/expenses/(.+)/delete', 'ExpensesDeleteHandler',
    '/expenses/import', 'ExpensesImportHandler',
)



application = web.application(urls, globals())
applicationinitializer(application)


class MainHandler(BaseHandler):
    def GET(self):
        if not self.current_user():
            return web.ctx.render.info()
        else:
            form = expenses_add()
            form.get('date').value = datetime.strftime(datetime.today(),
                    FORM_DATE_FORMAT)
            return web.ctx.render.index(user=self.current_user(),
                    expenses_add=form)



class LogoutHandler():
    def GET(self):
        web.setcookie('user', '', expires=time.time() - 86400)
        web.seeother('/')




if __name__ == '__main__':
    application.run()
