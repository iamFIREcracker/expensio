#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import urllib
import urlparse

import oauth2
import web

from app.config import COOKIE_EXPIRATION
from app.models import User
from app.utils import BaseHandler


TWITTER_APP_ID = "QSg3YnYAa6ha6msWlRzBFA"
TWITTER_APP_SECRET = "qJJBwVqUn100cD7phEnb211DNET1mmAWTC54fYSkmM"

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
AUTHORIZE_URL = 'https://api.twitter.com/oauth/authorize'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'


class LoginTwitterAuthorizedHandler(BaseHandler):
    def GET(self):
        if 'twitter_access_token' not in web.ctx.session:
            raise web.seeother('/')

        access_token = web.ctx.session.pop('twitter_access_token')
        user = self.current_user()
        if not user:
            user = web.ctx.orm.query(User).filter_by(
                    twitter_id=access_token['user_id'][-1]).first()

            if not user:
                user = User(name=access_token['screen_name'][-1])
        user.twitter_id = access_token['user_id'][-1]

        web.ctx.orm.add(user)
        # Merge fying and persistent object: this enables us to read the
        # automatically generated user id
        user = web.ctx.orm.merge(user)

        web.setcookie(
                'user', user.id, time.time() + COOKIE_EXPIRATION)
        raise web.seeother(
                '/users/%s/edit' % user.id if not self.current_user() else '/')


class LoginTwitterHandler():
    def GET(self):
        if 'twitter_access_token' in web.ctx.session:
            raise web.seeother(web.ctx.path_url + '/authorized')

        consumer = oauth2.Consumer(TWITTER_APP_ID, TWITTER_APP_SECRET)
        data = web.input(denied=None, oauth_token=None)

        if 'twitter_request_token' not in web.ctx.session:
            client = oauth2.Client(consumer)
            (resp, content) = client.request(REQUEST_TOKEN_URL, 'GET')
            if resp['status'] != '200':
                # XXX flash some message here
                web.debug(content)
                raise web.seeother('/')

            request_token = urlparse.parse_qs(content)
            web.ctx.session['twitter_request_token'] = request_token

        if data.denied:
            # The client denied permissions to the app
            web.ctx.session.pop('twitter_request_token')
            # XXX flash some message here
            raise web.seeother('/')

        if data.oauth_token is None:
            raise web.seeother(AUTHORIZE_URL + '?' + urllib.urlencode(
                    dict(oauth_token=request_token['oauth_token'][-1])))

        request_token = web.ctx.session.pop('twitter_request_token')
        token = oauth2.Token(request_token['oauth_token'][-1],
                request_token['oauth_token_secret'][-1])
        client = oauth2.Client(consumer, token)
        (resp, content) = client.request(ACCESS_TOKEN_URL, 'GET')
        if resp['status'] != '200':
            # XXX flash some message here
            web.debug(content)
            raise web.seeother('/')

        access_token = urlparse.parse_qs(content)
        web.ctx.session['twitter_access_token'] = access_token
        raise web.seeother(web.ctx.path_url + '/authorized')
