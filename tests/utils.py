#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import unittest

import web
import webtest


def temp_file():
    """Creates a temporary file."""
    return tempfile.NamedTemporaryFile(delete=False).name


def url(path):
    """Create a complete URL pointing to ``path``.

    Prepends protocol, domain and port numbers to ``path``"""
    return "http://localhost:80%(path)s" % dict(path=path)


def register(app):
    """Register a new user and return its id."""
    resp = login(app)
    return resp.forms[0]['id'].value


def login(app):
    """Register a new user and return its id."""
    resp = app.get('/login/fake')
    resp = resp.follow() # -> /login/fake/authorized
    return resp.follow() # -> /profile


def post_avatar_change(user_id, avatar, app):
    """Posts a new avatar change remote task."""
    resp = app.post(
            '/v1/users/%(user_id)s/avatar/change' % dict(user_id=user_id),
            dict(avatar=upload(avatar)), extra_environ=dict(
                HTTP_ACCEPT='application/json'
            ))
    return resp

def edit_profile(user_id, app, **data):
    """Updates profile."""
    resp = app.post(
            '/v1/users/%(user_id)s/edit' % dict(user_id=user_id),
            data, extra_environ=dict(HTTP_ACCEPT='application/json'))
    return resp


def upload(filename):
    """Return a webtest.Upload object for ``filename``.
    
    Note that ``filename`` is supposed to be relative."""
    return webtest.Upload(
            os.path.basename(os.path.abspath(filename)), file(filename).read())



class TestCaseWithApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dbfile = temp_file()

        # Configures the database
        # XXX Cannot move this below the import of ``init_db`` 
        web.config.db = 'sqlite:///' + cls.dbfile

        # Initialize the database
        from app.database import init_db
        init_db()

        # Configure celery
        #from app.celery import celery

        #celery.conf.update(
            ##BROKER_BACKEND='memory',
            #CELERY_ALWAYS_EAGER=True,
            #CELERY_EAGER_PROPAGATE_EXCEPTIONS=True
        #)

        # Create the application
        from app import create_app

        # Disable custom logging
        web.config.log_enable = False
        # Disable sql logging, otherwise webtest will consider them as errors
        web.config.debug_sql = False
        # Disable debug mode
        web.config.debug = False

        middleware = []
        cls.app = webtest.TestApp(create_app().wsgifunc(*middleware))

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.dbfile)


    def setUp(self):
        self.app.reset()
