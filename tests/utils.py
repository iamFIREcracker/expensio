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


def change_avatar(user_id, app, avatar=None):
    """Posts a new avatar change remove task."""
    data = dict() if avatar is None else dict(avatar=_upload(avatar))
    url = '/v1/users/%(user_id)s/avatar/change' % dict(user_id=user_id)
    resp = app.post(url, data,
                    extra_environ=dict(HTTP_ACCEPT='application/json'))
    return resp

def remove_avatar(user_id, app):
    """Removes the avatar associated with ``user_id``."""
    url = '/v1/users/%(user_id)s/avatar/remove' % dict(user_id=user_id)
    resp = app.post(url, extra_environ=dict(HTTP_ACCEPT='application/json'))
    return resp


def edit_profile(user_id, app, **data):
    """Updates profile."""
    resp = app.post(
            '/v1/users/%(user_id)s/edit' % dict(user_id=user_id),
            data, extra_environ=dict(HTTP_ACCEPT='application/json'))
    return resp

def delete_profile(user_id, app):
    """Deletes the user specified by ``user_id``."""
    resp = app.post(
            '/v1/users/%(user_id)s/delete' % dict(user_id=user_id),
            extra_environ=dict(HTTP_ACCEPT='application/json'))
    return resp

def _upload(filename):
    """Return a webtest.Upload object for ``filename``.
    
    Note that ``filename`` is supposed to be relative."""
    return webtest.Upload(
            os.path.basename(os.path.abspath(filename)), file(filename).read())



class TestCaseWithApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize the database
        from app.database import init_db
        init_db()

        # Create the application
        from app import create_app

        middleware = []
        cls.app = webtest.TestApp(create_app().wsgifunc(*middleware))

    def setUp(self):
        self.app.reset()
