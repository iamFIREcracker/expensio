#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import web

from models import AlchemyEncoder # XXX WTF?
from models import User


def jsonify(*args, **kwargs):
    web.header('Content-Type', 'application/json')

    return json.dumps(dict(*args, **kwargs), cls=AlchemyEncoder)



def protected(func):
    def inner(self, *args, **kwargs):
        if not self.current_user:
            raise web.unauthorized()

        return func(self, *args, **kwargs)
    return inner


def owner(model):
    def inner1(func):
        def inner2(self, id):
            record = (web.ctx.orm.query(model)
                    .filter_by(id=id)
                    .filter_by(user_id=self.current_user().id)
                    .first())
            if not record:
                raise web.notfound()

            setattr(self, '_current_item', record)

            return func(self, id)
        return inner2
    return inner1


def me(func):
    def inner1(self, id):
        if id != self.current_user().id:
            raise web.unauthorized()

        return func(self, id)
    return inner1



class BaseHandler(object):
    def current_user(self):
        if not hasattr(self, '_current_user'):
            self._current_user = None
            user_id = web.cookies().get('user')
            if user_id:
                self._current_user = (web.ctx.orm.query(User)
                        .filter_by(id=user_id).first())

        return self._current_user

    def current_item(self):
        if not hasattr(self, '_current_item'):
            self._current_item = None

        return self._current_item
