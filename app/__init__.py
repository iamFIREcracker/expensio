#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import web
from web.contrib.template import render_jinja

from app import config
from app import models
from app import sessions
from app.database import db_session
from .upload import UploadManager
from .urls import URLS


urls = URLS



working_dir = os.getcwd()
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
        web.ctx.orm.remove()
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
