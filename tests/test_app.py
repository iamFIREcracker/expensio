#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest
import tempfile

import web
from webtest import TestApp


def temp_file():
    """Creates a temporary file."""
    return tempfile.NamedTemporaryFile(suffix='.app.db', delete=False).name


def url(path):
    """Create a complete URL pointing to ``path``.

    Prepends protocol, domain and port numbers to ``path``"""
    return "http://localhost:80%(path)s" % dict(path=path)


def login(app):
    """Executes the login workflow."""
    resp = app.get('/login/fake')
    resp = resp.follow() # -> /login/fake/authorized
    resp = resp.follow() # -> /profile
    return resp


class TestApplication(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Disable sql logging, otherwise webtest will consider them as errors
        web.config.debug_sql = False

        # Configures the database
        cls.dbfile = temp_file()
        web.config.db = 'sqlite:///' + cls.dbfile

        # Initialize the database
        from app.database import init_db
        init_db()

        # Create the application
        from app import create_app
        middleware = []
        cls.app = TestApp(create_app().wsgifunc(*middleware))

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.dbfile)


    def test_anonymous_user_is_presented_with_the_info_page(self):
        resp = self.app.get('/')
        self.assertEquals('200 OK', resp.status)
        self.assertTrue(
                'Try it!' in resp, 'Fake register link missing')

    def test_logged_user_is_presented_the_main_page(self):
        login(self.app)
        resp = self.app.get('/')
        self.assertEquals('200 OK', resp.status)
        self.assertTrue(
                'Fake Name' in resp, 'Name of the user missing')
        self.assertTrue(
                'By Date' in resp, 'By-Date widget missing')
        self.assertTrue(
                'Income' in resp, 'Income widget missing')
        self.assertTrue(
                'Outcome' in resp, 'Outcome widget missing')
