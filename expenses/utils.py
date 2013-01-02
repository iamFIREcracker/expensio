#!/usr/bin/env python
# -*- coding: utf-8 -*-

import calendar
import os
import json
from datetime import date
from datetime import datetime

import web
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from web.contrib.template import render_jinja

import formatters
import parsers
from config import EPOCH
from config import DATABASE_SESSION_ENGINE
from models import engine
from models import AlchemyEncoder # XXX WTF?
from models import User
from upload import UploadManager



"""List of all the currencies available"""
_CURRENCIES = [u'€', u'$']

def currencies():
    """Return a list of all the supported currencies."""
    return _CURRENCIES


def applicationinitializer(application):
    working_dir = os.path.dirname(__file__)
    db = web.database(dbn='sqlite', db=DATABASE_SESSION_ENGINE.replace(
            'sqlite:///', ''))
    session = web.session.Session(
            application, web.session.DBStore(db, 'session'))

    def load_session():
        web.ctx.session = session;
    application.add_processor(web.loadhook(load_session))

    def load_path_url():
        web.ctx.path_url = web.ctx.home + web.ctx.path
    application.add_processor(web.loadhook(load_path_url))

    def load_sqla(handler):
        web.ctx.orm = scoped_session(sessionmaker(bind=engine))
        try:
            return handler()
        except web.HTTPError:
            web.ctx.orm.commit()
            raise
        except:
            web.ctx.orm.rollback()
            raise
        finally:
            web.ctx.orm.commit()
    application.add_processor(load_sqla)

    def load_render():
        render = render_jinja(os.path.join(working_dir, 'templates'),
                encoding='utf-8', extensions=['jinja2.ext.do'])
        web.ctx.render = render;
    application.add_processor(web.loadhook(load_render))

    def load_uploadmanager():
        uploadman = UploadManager(os.path.join(working_dir))
        web.ctx.uploadman = uploadman
    application.add_processor(web.loadhook(load_uploadmanager))


def jsonify(*args, **kwargs):
    web.header('Content-Type', 'application/json')

    return json.dumps(dict(*args, **kwargs), cls=AlchemyEncoder)


def parsedateparams():
    today = datetime.today()
    (_, days) = calendar.monthrange(today.year, today.month)
    startofmonth = date(today.year, today.month, 1)
    endsofmonth = date(today.year, today.month, days - 1)

    data = web.input(
            since=formatters.date(startofmonth),
            to=formatters.date(endsofmonth),
            latest=EPOCH)
    since = parsers.date(data.since)
    to = parsers.date(data.to)
    latest = parsers.datetime(data.latest)

    return (since, to, latest)


def protected(func):
    def inner(self, *args, **kwargs):
        if not self.current_user():
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


def active(func):
    def inner1(self, id):
        if self.current_item().deleted:
            raise web.unauthorized()

        return func(self, id)
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
        #web.seeother('/')
        pass
