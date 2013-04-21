#!/usr/bin/env python
# -*- coding: utf-8 -*-

import calendar
import json
import time
from datetime import date
from datetime import datetime

import web

import formatters
import parsers
import app.serializers as serializers

from app import config
from models import User



"""List of all the currencies available"""
_CURRENCIES = [u'€', u'$']

_FORMATS = ['tsv']


def get_name():
    """Gets the name of the application."""
    return config.APP_NAME


def get_version():
    """Gets the repository version."""
    import subprocess
    proc = subprocess.Popen(
            'hg log -r tip --template "{latesttagdistance}"',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pending, _ = proc.communicate()
    return "%(tag)sd%(pending)s" % dict(tag=config.TAG, pending=pending)


def currencies():
    """Return a list of all the supported currencies."""
    return _CURRENCIES


def formats():
    """Return a list of all the supported formats."""
    return _FORMATS


def compose(*funcs):
    """Compose functions, left to right"""
    def _compose(g, f):
        return  lambda *args, **kwargs: g(f(*args, **kwargs))
    return reduce(_compose, funcs)


def jsonify(*args, **kwargs):
    web.header('Content-Type', 'application/json')

    return json.dumps(dict(*args, **kwargs), cls=serializers.JSONSerializer)


def logout():
    web.setcookie('user', '', expires=time.time() - 86400)


def parsedateparams():
    today = datetime.today()
    (_, days) = calendar.monthrange(today.year, today.month)
    startofmonth = date(today.year, today.month, 1)
    endsofmonth = date(today.year, today.month, days - 1)

    data = web.input(
            since=formatters.date(startofmonth),
            to=formatters.date(endsofmonth),
            latest=config.EPOCH)
    since = parsers.date(data.since)
    to = parsers.date(data.to)
    latest = parsers.datetime(data.latest)

    return (since, to, latest)


def input_(**transformers):
    """Wrapper of `web.input` enabling users to execute validation and
    transformation of input data.

    TODO: add possibility to validate multiple fields together
    """
    defaults = dict((name, None) for name in transformers.iterkeys())
    storage = web.input(**defaults)

    def transform(name, value, func):
        try:
            return func(value)
        except:
            # TODO add some log here
            raise web.badrequest()

    [setattr(storage, name, transform(name, storage[name], transformers[name]))
            for (name, value) in storage.iteritems()]

    return storage
    

def api(func):
    def inner(self, *args, **kwargs):
        accept = web.ctx.environ.get('HTTP_ACCEPT', '').split(',')
        if 'application/json' not in accept:
            raise web.notacceptable()

        return func(self, *args, **kwargs)
    return inner


def protected(func):
    def inner(self, *args, **kwargs):
        if not self.current_user():
            raise web.unauthorized()

        return func(self, *args, **kwargs)
    return inner


def redirectable(func):
    def inner(self, *args, **kwargs):
        data = web.input(back=None)
        if data.back:
            web.ctx.session['back'] = data.back
        return func(self, *args, **kwargs)
    return inner


def owner(model, field='id'):
    def inner1(func):
        def inner2(self, value):
            record = (web.ctx.orm.query(model)
                    .filter_by(user_id=self.current_user().id)
                    .filter(getattr(model, field) == value)
                    .first())
            if not record:
                raise web.notfound()

            setattr(self, '_current_item', record)

            return func(self, id)
        return inner2
    return inner1


def active(func):
    def inner1(self, *args, **kwargs):
        if self.current_item().deleted:
            raise web.unauthorized()

        return func(self, *args, **kwargs)
    return inner1


def me(func):
    def inner1(self, id, *args, **kwargs):
        if id != self.current_user().id:
            raise web.unauthorized()

        return func(self, id, *args, **kwargs)
    return inner1



class BaseHandler(object):
    name = __name__

    def current_user(self):
        if not hasattr(self, '_current_user'):
            self._current_user = None
            user_id = web.cookies().get('user')
            if user_id:
                self._current_user = (web.ctx.orm.query(User)
                        .filter_by(id=user_id, deleted=False).first())

        return self._current_user

    def current_item(self):
        if not hasattr(self, '_current_item'):
            self._current_item = None

        return self._current_item


class UserUpdaterHandler(BaseHandler):
    def update(self, **kwargs):
        #user = self.current_user()
        #if not user:
            #user = web.ctx.orm.query(User).filter_by(
                    #google_id=profile['id']).first()
            #if not user:
                #user = User(name=profile["name"])
        #user.google_id = profile['id']

        #web.ctx.orm.add(user)
        ## Merge fying and persistent object: this enables us to read the
        ## automatically generated user id
        #user = web.ctx.orm.merge(user)

        #web.setcookie(
                #'user', user.id, expires=time.time() + 7 * 86400)
        #raise web.found('/')
        pass
