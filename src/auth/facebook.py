#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import urllib
import urlparse

import oauth2
import web

from config import COOKIE_EXPIRATION
from models import User
from utils import BaseHandler


FACEBOOK_APP_ID = "431016523607887"
FACEBOOK_APP_SECRET = "bcc5a62efaff20fc9808919b3e40a944"

AUTHORIZE_URL = 'https://www.facebook.com/dialog/oauth'
ACCESS_TOKEN_URL = 'https://graph.facebook.com/oauth/access_token'


class LoginFacebookAuthorizedHandler(BaseHandler):
    def GET(self):
        access_token = web.ctx.session.pop('facebook_access_token')
        profile = json.load(
                urllib.urlopen(
                    "https://graph.facebook.com/me?" +
                    urllib.urlencode(dict(
                        access_token=access_token['access_token'][-1]))))

        user = self.current_user()
        if not user:
            user = web.ctx.orm.query(User).filter_by(facebook_id=profile['id']).first()
            if not user:
                user = User(name=profile["name"])
        user.facebook_id = profile['id']

        web.ctx.orm.add(user)
        # Merge fying and persistent object: this enables us to read the
        # automatically generated user id
        user = web.ctx.orm.merge(user)

        web.setcookie(
                'user', user.id, time.time() + COOKIE_EXPIRATION)
        web.seeother('/')


class LoginFacebookHandler():
    def GET(self):
        if 'facebook_access_token' in web.ctx.session:
            web.seeother(web.ctx.path_url + '/authorized')
            return;

        data = web.input(error=None, code=None)

        if data.error:
            # The client denied permissions to the app
            # XXX flash some message here
            web.seeother('/')
            return

        if data.code is None:
            web.seeother(AUTHORIZE_URL + '?' + urllib.urlencode(
                dict(client_id=FACEBOOK_APP_ID, redirect_uri=web.ctx.path_url,
                    response_type='code', scope='')))
            return

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
            web.seeother('/')
            return

        access_token = urlparse.parse_qs(content)
        web.ctx.session['facebook_access_token'] = access_token
        web.seeother(web.ctx.path_url + '/authorized')
