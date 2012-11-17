#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urlparse

import oauth2
import web


FACEBOOK_APP_ID = "431016523607887"
FACEBOOK_APP_SECRET = "bcc5a62efaff20fc9808919b3e40a944"

AUTHORIZE_URL = 'https://www.facebook.com/dialog/oauth'
ACCESS_TOKEN_URL = 'https://graph.facebook.com/oauth/access_token'


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
