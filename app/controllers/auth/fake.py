#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import time
from datetime import datetime

import web

from app.models import User
from app.utils import BaseHandler
from app.config import COOKIE_EXPIRATION


class LoginFakeAuthorizedHandler(BaseHandler):
    def GET(self):
        if 'fake_access_token' not in web.ctx.session:
            web.seeother('/')
            return

        user = self.current_user()
        if not user:
            user = User(name='Fake Name')

        web.ctx.orm.add(user)
        # Merge fying and persistent object: this enables us to read the
        # automatically generated user id
        user = web.ctx.orm.merge(user)

        web.setcookie(
                'user', user.id, time.time() + COOKIE_EXPIRATION)
        web.seeother('/')


class LoginFakeHandler():
    def GET(self):
        if 'fake_access_token' in web.ctx.session:
            web.seeother(web.ctx.path_url + '/authorized')
            return

        web.ctx.session['fake_access_token'] = hashlib.sha256(
                str(datetime.now())).digest()
        web.seeother(web.ctx.path_url + '/authorized')
