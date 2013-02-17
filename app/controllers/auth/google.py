#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import urllib

import oauth2
import web

from app.config import COOKIE_EXPIRATION
from app.forms import users_connect
from app.models import User
from app.utils import jsonify
from app.utils import protected
from app.utils import redirectable
from app.utils import BaseHandler


GOOGLE_APP_ID = "694024250403.apps.googleusercontent.com"
GOOGLE_APP_SECRET = "vSuJRIdO2ujTmwORfdMT3AST"

AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/auth'
ACCESS_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'



class LoginGoogleAuthorizedHandler(BaseHandler):
    def GET(self):
        if 'google_access_token' not in web.ctx.session:
            raise web.found('/')

        access_token = web.ctx.session.pop('google_access_token')
        profile = json.load(
                urllib.urlopen(
                    "https://www.googleapis.com/oauth2/v1/userinfo?" +
                    urllib.urlencode(dict(
                        access_token=access_token['access_token']))))

        newuser = False
        user = self.current_user()
        if not user:
            user = web.ctx.orm.query(User).filter_by(
                    google_id=profile['id'], deleted=False).first()
            if not user:
                newuser = True
                user = User(name=profile["name"])
        user.google_id = profile['id']

        web.ctx.orm.add(user)
        # Merge fying and persistent object: this enables us to read the
        # automatically generated user id
        user = web.ctx.orm.merge(user)

        web.setcookie(
                'user', user.id, time.time() + COOKIE_EXPIRATION)

        raise web.found(
                web.ctx.session.pop('back') if 'back' in web.ctx.session else
                '/profile' if newuser else '/')


class LoginGoogleHandler():
    @redirectable
    def GET(self):
        if 'google_access_token' in web.ctx.session:
            raise web.found(web.ctx.path_url + '/authorized')

        data = web.input(error=None, code=None)

        if data.error:
            # The client denied permissions to the app
            # XXX flash some message here
            raise web.found('/')

        if data.code is None:
            raise web.found(AUTHORIZE_URL + '?' + urllib.urlencode(
                dict(client_id=GOOGLE_APP_ID, redirect_uri=web.ctx.path_url,
                    response_type='code',
                    scope='https://www.googleapis.com/auth/userinfo.profile')))

        consumer = oauth2.Consumer(GOOGLE_APP_ID, GOOGLE_APP_SECRET)
        client = oauth2.Client(consumer)
        (resp, content) = client.request(ACCESS_TOKEN_URL, 'POST',
                urllib.urlencode(dict(code=data.code, client_id=GOOGLE_APP_ID,
                    client_secret=GOOGLE_APP_SECRET,
                    redirect_uri=web.ctx.path_url,
                    grant_type='authorization_code')))
        if resp['status'] != '200':
            # XXX flash some message here
            web.debug(content)
            raise web.found('/')

        access_token = json.loads(content)
        web.ctx.session['google_access_token'] = access_token
        raise web.found(web.ctx.path_url + '/authorized')


class AccountsGoogleDisconnectHandler(BaseHandler):
    @protected
    def POST(self):
        user = self.current_user()
        user.google_id = None
        connect = users_connect()
        if not connect.validates(
                google=(user.google_id is not None),
                facebook=(user.facebook_id is not None),
                twitter=(user.twitter_id is not None)):
            return jsonify(success=False, reason=connect.note)

        web.ctx.orm.add(user)
        return jsonify(success=True)
