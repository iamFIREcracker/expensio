#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import web

from app import config
from app import models
from app import sessions
from app.database import db_session
from app.logging import create_logger
from .tools.app_processor import load_keyvalue
from .tools.app_processor import load_logger
from .tools.app_processor import load_path_url
from .tools.app_processor import load_render
from .tools.app_processor import load_session
from .tools.app_processor import load_sqla
from .export import ExportManager
from .upload import UploadManager
from .urls import URLS


web.config.logger_name = config.LOGGER_NAME
web.config.log_format = config.LOG_FORMAT
web.config.debug = config.DEBUG
web.config.debug_sql = config.DEBUG_SQL

workingdir = os.getcwd()
app = web.application(URLS, globals())
dbpath = config.DATABASE_URL.replace('sqlite:///', '')
db = web.database(dbn='sqlite', db=dbpath)
session = web.session.Session(app, web.session.DBStore(db, 'session'))

app.add_processor(web.loadhook(load_path_url))
app.add_processor(web.loadhook(load_logger(create_logger(web.config))))
app.add_processor(web.loadhook(load_render(workingdir)))
app.add_processor(web.loadhook(load_session(session)))
app.add_processor(web.loadhook(load_keyvalue('uploadman',
                                             UploadManager(config.UPLOAD_DIR,
                                                           workingdir))))
app.add_processor(web.loadhook(load_keyvalue('avatarman',
                                             UploadManager(config.AVATAR_DIR,
                                                           workingdir))))
app.add_processor(web.loadhook(load_keyvalue('exportman',
                                             ExportManager(workingdir))))
app.add_processor(load_sqla(db_session))
