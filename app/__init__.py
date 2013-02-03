#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import web

from app import config
from app import models
from app import sessions
from app.database import db_session
from .tools.app_processor import load_keyvalue
from .tools.app_processor import load_path_url
from .tools.app_processor import load_render
from .tools.app_processor import load_session
from .tools.app_processor import load_sqla
from .export import ExportManager
from .upload import UploadManager
from .urls import URLS


urls = URLS



workingdir = os.getcwd()
app = web.application(urls, globals())
dbpath = config.DATABASE_URL.replace('sqlite:///', '')
db = web.database(dbn='sqlite', db=dbpath)
session = web.session.Session(app, web.session.DBStore(db, 'session'))

app.add_processor(web.loadhook(load_path_url))
app.add_processor(web.loadhook(load_render(workingdir)))
app.add_processor(web.loadhook(load_session(session)))
app.add_processor(web.loadhook(load_keyvalue('uploadman',
                                             UploadManager(workingdir))))
app.add_processor(web.loadhook(load_keyvalue('exportman',
                                             ExportManager(workingdir))))
app.add_processor(load_sqla(db_session))
