#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import unicode_literals

import os
import time
from datetime import datetime

import web
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from web.contrib.template import render_jinja

from amounts import AmountsHandler
from auth import LoginGoogleHandler
from auth import LoginGoogleAuthorizedHandler
from auth import LoginFacebookHandler
from auth import LoginFacebookAuthorizedHandler
from auth import LoginTwitterHandler
from auth import LoginTwitterAuthorizedHandler
from categories import CategoriesHandler
from expenses import ExpensesHandler
from expenses import ExpensesAddHandler
from expenses import ExpensesEditHandler
from expenses import ExpensesDeleteHandler
from expenses import ExpensesImportHandler
from filters import datetimeformat
from filters import cashformat
from forms import expenses_add
from forms import users_edit
from forms import FORM_DATE_FORMAT
from models import engine
from utils import me
from utils import protected
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

    '/amounts.json', 'AmountsHandler',

    '/categories.json', 'CategoriesHandler',

    '/expenses.json', 'ExpensesHandler',
    '/expenses/add', 'ExpensesAddHandler',
    '/expenses/(.+)/edit', 'ExpensesEditHandler',
    '/expenses/(.+)/delete', 'ExpensesDeleteHandler',
    '/expenses/import', 'ExpensesImportHandler',
)



application = web.application(urls, globals())
session = web.session.Session(application, web.session.DiskStore('sessions'))

def load_session():
    web.ctx.session = session
application.add_processor(web.loadhook(load_session))

def load_path_url():
    web.ctx.path_url = web.ctx.home + web.ctx.path
application.add_processor(web.loadhook(load_path_url))

def load_sqla(handler):
    web.ctx.orm = scoped_session(sessionmaker(bind=engine))
    try:
        return handler()
    except web.HTTPError:
       web.ctx.orm.commit()
       raise
    except:
        web.ctx.orm.rollback()
        raise
    finally:
        web.ctx.orm.commit()
application.add_processor(load_sqla)

def load_render():
    working_dir = os.path.dirname(__file__)
    render = render_jinja(os.path.join(working_dir, 'templates'),
            encoding='utf-8', extensions=['jinja2.ext.do'])

    render._lookup.filters.update(
            datetime=datetimeformat, cash=cashformat)
    web.ctx.render = render;
application.add_processor(web.loadhook(load_render))



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



class UsersEditHandler(BaseHandler):
    @protected
    @me
    def GET(self, id):
        form = users_edit()
        user = self.current_user()
        form.fill(id=user.id, name=user.name, currency=user.currency)
        return web.ctx.render.users_edit_complete(users_edit=form)

    @protected
    @me
    def POST(self, id):
        form = users_edit()
        if form.validates():
            u = self.current_user()
            u.name = form.d.name
            u.currency = form.d.currency
            web.ctx.orm.add(u)
        return web.ctx.render.users_edit(users_edit=form)



if __name__ == '__main__':
    application.run()
