#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import random
import time
from datetime import timedelta
from datetime import datetime

import web

from app.forms import users_connect
from app.models import Expense
from app.models import User
from app.utils import jsonify
from app.utils import protected
from app.utils import redirectable
from app.utils import BaseHandler
from app.config import COOKIE_EXPIRATION


class LoginFakeAuthorizedHandler(BaseHandler):
    def GET(self):
        newuser = False
        user = self.current_user()
        if not user:
            newuser = True
            user = User(name='Fake Name')

        web.ctx.orm.add(user)
        # Merge fying and persistent object: this enables us to read the
        # automatically generated user id
        user = web.ctx.orm.merge(user)

        web.setcookie(
                'user', user.id, time.time() + COOKIE_EXPIRATION)

        dates = [datetime.today() - timedelta(i) for i in range(1000)]
        categories = 'foo bar baz qux quux corge grault'.split()
        notes = [s.strip() for s in '''Past the sticky heritage relaxes a waved aunt.
                                       A widest noise resigns a barred cue.
                                       When can the patience stagger?
                                       A vowel beards the victory.
                                       Her market damages the disposable anarchy.
                                       An alcoholic release mounts the preferable routine.
                                       The mighty concentrate breathes within the muddle.'''.split('\n')]
        amounts = range(1, 40)
        web.ctx.orm.add_all(
                Expense(user_id=user.id, date=random.choice(dates),
                        category=random.choice(categories),
                        note=random.choice(notes),
                        amount=random.choice(amounts)) for _ in xrange(1000))

        raise web.found(
                web.ctx.session.pop('back') if 'back' in web.ctx.session else
                '/profile' if newuser else '/')


class LoginFakeHandler():
    @redirectable
    def GET(self):
        if 'fake_access_token' in web.ctx.session:
            raise web.found(web.ctx.path_url + '/authorized')

        web.ctx.session['fake_access_token'] = hashlib.sha256(
                str(datetime.now())).digest()
        raise web.found(web.ctx.path_url + '/authorized')


class AccountsFakeDisconnectHandler(BaseHandler):
    @protected
    def POST(self):
        user = self.current_user()
        connect = users_connect()
        if not connect.validates(
                google=(user.google_id is not None),
                facebook=(user.facebook_id is not None),
                twitter=(user.twitter_id is not None)):
            return jsonify(success=False, reason=connect.note)

        return jsonify(success=True)
