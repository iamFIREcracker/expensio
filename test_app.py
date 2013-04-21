#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest
import tempfile

import web
from webtest import TestApp


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
        # Disable sql logging, otherwise webtest would consider log messages
        # as errors :-(
        web.config.debug_sql = False

        # Configures the database to use (in memory for tests)
        cls.dbfile = tempfile.NamedTemporaryFile(suffix='app', delete=False).name
        web.config.db = 'sqlite:///' + cls.dbfile
        raise ValueError(web.config.db)

        # Initialize the database
        import app.database as database
        database.init_db()

        # Create the application
        from app import create_app
        middleware = []
        cls.app = TestApp(create_app().wsgifunc(*middleware))

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.dbfile)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_anonymous_user_is_presented_with_the_info_page(self):
        resp = self.app.get('/')
        self.assertEquals('200 OK', resp.status)
        self.assertTrue(
                'Try it!' in resp, "The page should contain a ``Try it!`` message.")

    def test_new_user_is_presented_with_the_profile_page(self):
        resp = self.app.get('/login/fake')
        self.assertEquals('302 Found', resp.status)
        self.assertEquals(url('/login/fake/authorized'), resp.location)
        resp = resp.follow()
        self.assertEquals('302 Found', resp.status)
        self.assertEquals(url('/profile'), resp.location)
        resp = resp.follow()
        self.assertEquals('200 OK', resp.status)
        self.assertTrue(
                'Profile' in resp, "The page should contain a ``Profile`` message.")

