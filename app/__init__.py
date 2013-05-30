#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import web

from app import config


web.config.debug = config.DEBUG
web.config.debug_sql = config.DEBUG_SQL

web.config.logger_name = config.LOGGER_NAME
web.config.log_enable = config.LOG_ENABLE
web.config.log_format = config.LOG_FORMAT

web.config.db = config.DATABASE_URL

web.config.FACEBOOK_APP_ID = config.FACEBOOK_APP_ID
web.config.FACEBOOK_APP_SECRET = config.FACEBOOK_APP_SECRET
web.config.GOOGLE_APP_ID = config.GOOGLE_APP_ID
web.config.GOOGLE_APP_SECRET = config.GOOGLE_APP_SECRET
web.config.TWITTER_APP_ID = config.TWITTER_APP_ID
web.config.TWITTER_APP_SECRET = config.TWITTER_APP_SECRET
web.config.TWITTER_APP_CALLBACK = config.TWITTER_APP_CALLBACK


def create_app():
    """App factory."""
    from app.database import create_session
    from app.logging import create_logger
    from app.tools.app_processor import load_keyvalue
    from app.tools.app_processor import load_logger
    from app.tools.app_processor import load_path_url
    from app.tools.app_processor import load_render
    from app.tools.app_processor import load_session
    from app.tools.app_processor import load_sqla
    from app.tools.app_processor import manage_content_exceptions
    from app.export import ExportManager
    from app.upload import UploadManager
    from app.urls import URLS

    workingdir = os.getcwd()
    views = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'views')
    app = web.application(URLS, globals())
    dbpath = web.config.db.replace('sqlite:///', '')
    db = web.database(dbn='sqlite', db=dbpath)
    session = web.session.Session(app, web.session.DBStore(db, 'session'))

    uploadman = UploadManager(config.UPLOAD_DIR, workingdir)
    avatarman = UploadManager(config.AVATAR_DIR, workingdir)
    exportman = ExportManager(workingdir)

    app.add_processor(web.loadhook(load_path_url))
    app.add_processor(web.loadhook(load_logger(create_logger(web.config))))
    app.add_processor(web.loadhook(load_render(views)))
    app.add_processor(web.loadhook(load_session(session)))
    app.add_processor(web.loadhook(load_keyvalue('uploadman', uploadman)))
    app.add_processor(web.loadhook(load_keyvalue('avatarman', avatarman)))
    app.add_processor(web.loadhook(load_keyvalue('exportman', exportman)))
    app.add_processor(load_sqla(create_session()))
    app.add_processor(manage_content_exceptions)

    return app
