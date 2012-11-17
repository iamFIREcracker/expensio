#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urlparse

import oauth2
import web


TWITTER_APP_ID = "QSg3YnYAa6ha6msWlRzBFA"
TWITTER_APP_SECRET = "qJJBwVqUn100cD7phEnb211DNET1mmAWTC54fYSkmM"

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
AUTHORIZE_URL = 'https://api.twitter.com/oauth/authorize'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'



class LoginTwitterHandler():
    def GET(self):
        if 'twitter_access_token' in web.ctx.session:
            web.seeother(web.ctx.path_url + '/authorized')
            return

        consumer = oauth2.Consumer(TWITTER_APP_ID, TWITTER_APP_SECRET)
        data = web.input(denied=None, oauth_token=None)

        if 'twitter_request_token' not in web.ctx.session:
            client = oauth2.Client(consumer)
            (resp, content) = client.request(REQUEST_TOKEN_URL, 'GET')
            if resp['status'] != '200':
                # XXX flash some message here
                web.debug(content)
                web.seeother('/')
                return

            request_token = urlparse.parse_qs(content)
            web.ctx.session['twitter_request_token'] = request_token

        if data.denied:
            # The client denied permissions to the app
            web.ctx.session.pop('twitter_request_token')
            # XXX flash some message here
            web.seeother('/')
            return

        if data.oauth_token is None:
            web.seeother(AUTHORIZE_URL + '?' + urllib.urlencode(
                    dict(oauth_token=request_token['oauth_token'][-1])))
            return

        request_token = web.ctx.session.pop('twitter_request_token')
        token = oauth2.Token(request_token['oauth_token'][-1],
                request_token['oauth_token_secret'][-1])
        client = oauth2.Client(consumer, token)
        (resp, content) = client.request(ACCESS_TOKEN_URL, 'GET')
        if resp['status'] != '200':
            # XXX flash some message here
            web.debug(content)
            web.seeother('/')
            return

        access_token = urlparse.parse_qs(content)
        web.ctx.session['twitter_access_token'] = access_token
        web.seeother(web.ctx.path_url + '/authorized')
