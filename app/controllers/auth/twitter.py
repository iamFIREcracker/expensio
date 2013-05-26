#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urlparse

import oauth2
import web

from app.config import COOKIE_EXPIRATION
from app.forms import users_connect
from app.models import User
from app.utils import jsonify
from app.utils import protected
from app.utils import redirectable
from app.utils import BaseHandler


REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
AUTHORIZE_URL = 'https://api.twitter.com/oauth/authorize'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'


class LoginTwitterAuthorizedHandler(BaseHandler):
    def GET(self):
        if 'twitter_access_token' not in web.ctx.session:
            raise web.found('/')

        access_token = web.ctx.session.pop('twitter_access_token')

        newuser = False
        user = self.current_user()
        if not user:
            user = web.ctx.orm.query(User).filter_by(
                    twitter_id=access_token['user_id'][-1],
                    deleted=False).first()
            if not user:
                newuser = True
                user = User(name=access_token['screen_name'][-1])
        user.twitter_id = access_token['user_id'][-1]

        web.ctx.orm.add(user)
        web.ctx.orm.commit()
        # Merge fying and persistent object: this enables us to read the
        # automatically generated user id
        user = web.ctx.orm.merge(user)

        web.setcookie('user', user.id, COOKIE_EXPIRATION)

        raise web.found(
                web.ctx.session.pop('back') if 'back' in web.ctx.session else
                '/profile' if newuser else '/')


class LoginTwitterHandler():
    @redirectable
    def GET(self):
        if 'twitter_access_token' in web.ctx.session:
            raise web.found(web.ctx.path_url + '/authorized')

        consumer = oauth2.Consumer(web.config.TWITTER_APP_ID,
                                   web.config.TWITTER_APP_SECRET)
        data = web.input(denied=None, oauth_token=None, back=None)

        if 'twitter_request_token' not in web.ctx.session:
            client = oauth2.Client(consumer)
            (resp, content) = client.request(REQUEST_TOKEN_URL, 'GET')
            if resp['status'] != '200':
                # XXX flash some message here
                web.debug(content)
                raise web.found('/')

            request_token = urlparse.parse_qs(content)
            web.ctx.session['twitter_request_token'] = request_token

        if data.denied:
            # The client denied permissions to the app
            web.ctx.session.pop('twitter_request_token')
            # XXX flash some message here
            raise web.found('/')

        if data.oauth_token is None:
            raise web.found(AUTHORIZE_URL + '?' + urllib.urlencode(
                    dict(oauth_token=request_token['oauth_token'][-1])))

        request_token = web.ctx.session.pop('twitter_request_token')
        token = oauth2.Token(request_token['oauth_token'][-1],
                request_token['oauth_token_secret'][-1])
        client = oauth2.Client(consumer, token)
        (resp, content) = client.request(ACCESS_TOKEN_URL, 'GET')
        if resp['status'] != '200':
            # XXX flash some message here
            web.debug(content)
            raise web.found('/')

        access_token = urlparse.parse_qs(content)
        web.ctx.session['twitter_access_token'] = access_token
        raise web.found(web.ctx.path_url + '/authorized')


class AccountsTwitterDisconnectHandler(BaseHandler):
    @protected
    def POST(self):
        user = self.current_user()
        user.twitter_id = None
        connect = users_connect()
        if not connect.validates(
                google=(user.google_id is not None),
                facebook=(user.facebook_id is not None),
                twitter=(user.twitter_id is not None)):
            return jsonify(success=False, reason=connect.note)

        web.ctx.orm.add(user)
        web.ctx.orm.commit()
        return jsonify(success=True)
