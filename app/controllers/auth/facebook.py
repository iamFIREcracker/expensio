#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import urllib
import urlparse

import oauth2
import web

from app.config import COOKIE_EXPIRATION
from app.models import User
from app.utils import BaseHandler


FACEBOOK_APP_ID = "431016523607887"
FACEBOOK_APP_SECRET = "bcc5a62efaff20fc9808919b3e40a944"

AUTHORIZE_URL = 'https://www.facebook.com/dialog/oauth'
ACCESS_TOKEN_URL = 'https://graph.facebook.com/oauth/access_token'


class LoginFacebookAuthorizedHandler(BaseHandler):
    def GET(self):
        if 'facebook_access_token' not in web.ctx.session:
            raise web.found('/')

        access_token = web.ctx.session.pop('facebook_access_token')
        profile = json.load(
                urllib.urlopen(
                    "https://graph.facebook.com/me?" +
                    urllib.urlencode(dict(
                        access_token=access_token['access_token'][-1]))))

        newuser = False
        user = self.current_user()
        if not user:
            user = web.ctx.orm.query(User).filter_by(
                    facebook_id=profile['id'], deleted=False).first()
            if not user:
                newuser = True
                user = User(name=profile["name"])
        user.facebook_id = profile['id']

        web.ctx.orm.add(user)
        # Merge fying and persistent object: this enables us to read the
        # automatically generated user id
        user = web.ctx.orm.merge(user)

        web.setcookie(
                'user', user.id, time.time() + COOKIE_EXPIRATION)
        raise web.found(
                '/users/%s/edit' % user.id if newuser else '/')


class LoginFacebookHandler():
    def GET(self):
        if 'facebook_access_token' in web.ctx.session:
            raise web.found(web.ctx.path_url + '/authorized')

        data = web.input(error=None, code=None)

        if data.error:
            # The client denied permissions to the app
            # XXX flash some message here
            raise web.found('/')

        if data.code is None:
            raise web.found(AUTHORIZE_URL + '?' + urllib.urlencode(
                dict(client_id=FACEBOOK_APP_ID, redirect_uri=web.ctx.path_url,
                    response_type='code', scope='')))

        consumer = oauth2.Consumer(FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
        client = oauth2.Client(consumer)
        (resp, content) = client.request(ACCESS_TOKEN_URL + '?'
                + urllib.urlencode(dict(code=data.code,
                    client_id=FACEBOOK_APP_ID,
                    client_secret=FACEBOOK_APP_SECRET,
                    redirect_uri=web.ctx.path_url)), 'GET')
        if resp['status'] != '200':
            # XXX flash some message here
            web.debug(content)
            raise web.found('/')

        access_token = urlparse.parse_qs(content)
        web.ctx.session['facebook_access_token'] = access_token
        raise web.found(web.ctx.path_url + '/authorized')
