#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib

import oauth2
import web


GOOGLE_APP_ID = "694024250403.apps.googleusercontent.com"
GOOGLE_APP_SECRET = "vSuJRIdO2ujTmwORfdMT3AST"

AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/auth'
ACCESS_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'

class LoginGoogleHandler():
    def GET(self):
        if 'google_access_token' in web.ctx.session:
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
                dict(client_id=GOOGLE_APP_ID, redirect_uri=web.ctx.path_url,
                    response_type='code',
                    scope='https://www.googleapis.com/auth/userinfo.profile')))
            return

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
            web.seeother('/')
            return

        access_token = json.loads(content)
        web.ctx.session['google_access_token'] = access_token
        web.seeother(web.ctx.path_url + '/authorized')
