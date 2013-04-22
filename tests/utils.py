#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import unittest

import web
import webtest


def temp_file():
    """Creates a temporary file."""
    return tempfile.NamedTemporaryFile(suffix='.app.db', delete=False).name


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


def upload(filename):
    """Return a webtest.Upload object for ``filename``.
    
    Note that ``filename`` is supposed to be relative."""
    return webtest.Upload(
            os.path.basename(os.path.abspath(filename)), file(filename).read())



class TestCaseWithApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Disable custom logging
        web.config.log_enable = False
        # Disable sql logging, otherwise webtest will consider them as errors
        web.config.debug_sql = False
        # Disable debug mode
        web.config.debug = False

        # Configures the database
        cls.dbfile = temp_file()
        web.config.db = 'sqlite:///' + cls.dbfile

        # Initialize the database
        from app.database import init_db
        init_db()

        # Create the application
        from app import create_app
        middleware = []
        cls.app = webtest.TestApp(create_app().wsgifunc(*middleware))

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.dbfile)


    def setUp(self):
        self.app.reset()
