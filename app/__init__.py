#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

import web
from web.contrib.template import render_jinja
from werkzeug.debug import DebuggedApplication

from app import config
from app import models
from app import sessions
from app.database import db_session
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
from utils import BaseHandler
from upload import UploadManager


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



working_dir = os.path.dirname(__file__)

app = web.application(urls, globals())
dbpath = config.DATABASE_URL.replace('sqlite:///', '')
db = web.database(dbn='sqlite', db=dbpath)
session = web.session.Session(app,
                                web.session.DBStore(db, 'session'))

def load_session():
    web.ctx.session = session;
app.add_processor(web.loadhook(load_session))

def load_path_url():
    web.ctx.path_url = web.ctx.home + web.ctx.path
app.add_processor(web.loadhook(load_path_url))

def load_sqla(handler):
    web.ctx.orm = db_session

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
        #web.ctx.orm.remove()
app.add_processor(load_sqla)

def load_render():
    render = render_jinja(os.path.join(working_dir, 'templates'),
            encoding='utf-8', extensions=['jinja2.ext.do'])
    web.ctx.render = render;
app.add_processor(web.loadhook(load_render))

def load_uploadmanager():
    uploadman = UploadManager(os.path.join(working_dir))
    web.ctx.uploadman = uploadman
app.add_processor(web.loadhook(load_uploadmanager))
