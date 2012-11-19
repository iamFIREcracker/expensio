﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import unicode_literals

import json
import os
import time
import urllib
from datetime import datetime
from datetime import timedelta

import web
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import extract
from sqlalchemy import func
from web.contrib.template import render_jinja

from auth import LoginGoogleHandler
from auth import LoginFacebookHandler
from auth import LoginTwitterHandler
from config import LATEST_DAYS_DATE_FORMAT
from config import DATE_FORMAT
from config import EPOCH
from filters import datetimeformat
from filters import cashformat
from forms import expenses_add
from forms import expenses_edit
from forms import expenses_import
from forms import users_edit
from forms import FORM_DATE_FORMAT
from forms import FORM_PERIOD_FORMAT
from models import engine
from models import AlchemyEncoder
from models import Expense
from models import User



SECONDS_TO_DAYS = 60 * 60 * 24

urls = (
    '/', 'MainHandler',

    '/login/google', 'LoginGoogleHandler',
    '/login/google/authorized', 'LoginGoogleAuthorizedHandler',
    '/login/facebook', 'LoginFacebookHandler',
    '/login/facebook/authorized', 'LoginFacebookAuthorizedHandler',
    '/login/twitter', 'LoginTwitterHandler',
    '/login/twitter/authorized', 'LoginTwitterAuthorizedHandler',
    '/logout', 'LogoutHandler',

    '/users/(.+)/edit', 'UsersEditHandler',

    '/amounts.json', 'AmountsHandler',

    '/expenses.json', 'ExpensesHandler',
    '/expenses/add', 'ExpensesAddHandler',
    '/expenses/(.+)/edit', 'ExpensesEditHandler',
    '/expenses/(.+)/delete', 'ExpensesDeleteHandler',
    '/expenses/import', 'ExpensesImportHandler',
)




application = web.application(urls, globals())

session = web.session.Session(application, web.session.DiskStore('sessions'))

def load_session():
    web.ctx.session = session
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

working_dir = os.path.dirname(__file__)
render = render_jinja(os.path.join(working_dir, 'templates'),
        encoding='utf-8', extensions=['jinja2.ext.do'])
render._lookup.filters.update(
        datetime=datetimeformat, cash=cashformat)


def jsonify(*args, **kwargs):
    web.header('Content-Type', 'application/json')

    return json.dumps(dict(*args, **kwargs), cls=AlchemyEncoder)


def protected(func):
    def inner(self, *args, **kwargs):
        if not self.current_user():
            web.seeother('/')
            return

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


class ExpenseWrapper(object):
    __serializable__ = {
            'id': lambda o: o.e.id,
            'date': lambda o: datetime.strftime(o.e.date, DATE_FORMAT),
            'created': lambda o: datetime.strftime(o.e.created, DATE_FORMAT),
            'updated': lambda o: datetime.strftime(o.e.updated, DATE_FORMAT),
            'category': lambda o: o.e.category,
            'amount': lambda o: float(o.e.amount),
            'currency': lambda o: o.currency,
            'note': lambda o: o.e.note,
            'deleted': lambda o: bool(o.e.deleted),
            }

    def __init__(self, expense, currency):
        self.e = expense
        self.currency = currency


class Category(object):
    __serializable__ = {
        'name': lambda o: o.c[0],
        'amount': lambda o: o.c[1],
        'currency': lambda o: o.currency,
        }

    def __init__(self, category, currency):
        self.c = category
        self.currency = currency


class Day(object):
    __serializable__ = {
            'date': lambda o: o.d[0],
            'updated': lambda o: datetime.strftime(o.d[1], DATE_FORMAT),
            'delta': lambda o: int(o.d[2]),
            'amount': lambda o: o.d[3],
            'currency': lambda o: o.currency,
            }

    def __init__(self, day, currency):
        self.d = day
        self.currency = currency



class BaseHandler():
    def current_user(self):
        """Returns the logged in Facebook user or None."""

        if not hasattr(self, "_current_user"):
            self._current_user = None
            user_id = web.cookies().get('user')
            if user_id:
                self._current_user = (web.ctx.orm.query(User)
                        .filter_by(id=user_id).first())

        return self._current_user


class ItemHandler():
    def current_item(self):
        return self._current_item



class MainHandler(BaseHandler):
    def GET(self):
        if not self.current_user():
            return render.info()
        else:
            form = expenses_add()
            form.get('date').value = datetime.strftime(datetime.today(),
                    FORM_DATE_FORMAT)
            return render.index(user=self.current_user(),
                    expenses_add=form)



class LoginGoogleAuthorizedHandler(BaseHandler):
    def GET(self):
        access_token = web.ctx.session.pop('google_access_token')
        profile = json.load(
                urllib.urlopen(
                    "https://www.googleapis.com/oauth2/v1/userinfo?" +
                    urllib.urlencode(dict(
                        access_token=access_token['access_token']))))

        user = self.current_user()
        if not user:
            user = web.ctx.orm.query(User).filter_by(google_id=profile['id']).first()
            if not user:
                user = User(name=profile["name"])
        user.google_id = profile['id']

        web.ctx.orm.add(user)
        # Merge fying and persistent object: this enables us to read the
        # automatically generated user id
        user = web.ctx.orm.merge(user)

        web.setcookie(
                'user', user.id, expires=time.time() + 7 * 86400)
        web.seeother('/')


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
                'user', user.id, expires=time.time() + 7 * 86400)
        web.seeother('/')


class LoginTwitterAuthorizedHandler(BaseHandler):
    def GET(self):
        if 'twitter_access_token' not in web.ctx.session:
            web.seeother('/')
            return

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
                'user', user.id, expires=time.time() + 7 * 86400)
        web.seeother('/')


class LogoutHandler():
    def GET(self):
        web.setcookie('user', '', expires=time.time() - 86400)
        web.seeother('/')



class UsersEditHandler(BaseHandler):
    @protected
    @me
    def GET(self, id):
        form = users_edit()
        user = self.current_user()
        form.fill(id=user.id, name=user.name, currency=user.currency)
        return render.users_edit_complete(users_edit=form)

    @protected
    @me
    def POST(self, id):
        form = users_edit()
        if form.validates():
            u = self.current_user()
            u.name = form.d.name
            u.currency = form.d.currency
            web.ctx.orm.add(u)
        return render.users_edit(users_edit=form)



class AmountsHandler(BaseHandler):
    @protected
    def GET(self):
        today = datetime.today()
        data = web.input(days=30, latest=EPOCH)
        user_id = self.current_user().id

        days = int(data.days)
        latest = datetime.strptime(data.latest if data.latest else EPOCH, DATE_FORMAT)

        past = today - timedelta(days - 1)

        expenses = (web.ctx.orm.query(Expense)
                .filter_by(user_id=user_id)
                .filter(Expense.date >= past)
                .filter(Expense.date <= today)
                .filter(Expense.updated > latest)
                .order_by(Expense.date.desc())
                .all())

        days = [] if not expenses else (
                web.ctx.orm.query(
                        func.strftime(LATEST_DAYS_DATE_FORMAT, Expense.date),
                        func.max(Expense.updated),
                        (func.strftime("%s", Expense.date) - func.strftime("%s", today)) / SECONDS_TO_DAYS,
                        func.sum(Expense.amount))
                    .filter_by(user_id=user_id)
                    .filter(Expense.date.in_((e.date for e in expenses)))
                    .group_by(func.strftime(LATEST_DAYS_DATE_FORMAT, Expense.date))
                    .all())

        return jsonify(days=[Day(d, self.current_user().currency) for d in days])


class ExpensesHandler(BaseHandler):
    @protected
    def GET(self):
        today = datetime.today()
        data = web.input(year=today.year, month=today.month,
                latest=EPOCH)
        user_id = self.current_user().id

        year = int(data.year)
        month = int(data.month)
        latest = datetime.strptime(data.latest if data.latest else EPOCH, DATE_FORMAT)

        expenses = (web.ctx.orm.query(Expense)
                .filter_by(user_id=user_id)
                .filter(extract('year', Expense.date) == year)
                .filter(extract('month', Expense.date) == month)
                .filter(Expense.updated > latest)
                .order_by(Expense.date.desc())
                .all())

        categories = [] if not expenses else (
                web.ctx.orm.query(Expense.category, func.sum(Expense.amount))
                    .filter_by(user_id=user_id)
                    .filter(extract('year', Expense.date) == year)
                    .filter(extract('month', Expense.date) == month)
                    .filter(Expense.category.in_((e.category for e in expenses)))
                    .order_by(Expense.category)
                    .group_by(Expense.category)
                    .all())

        return jsonify(expenses=[ExpenseWrapper(e, self.current_user().currency) for e in expenses],
                categories=[Category(c, self.current_user().currency) for c in categories])


class ExpensesAddHandler(BaseHandler):
    @protected
    def POST(self):
        form = expenses_add()
        if form.validates():
            e = Expense(user_id=self.current_user().id,
                    amount=float(form.d.amount), category=form.d.category,
                    note=form.d.note,
                    date=datetime.strptime(form.d.date, FORM_DATE_FORMAT))
            web.ctx.orm.add(e)
        return render.expenses_add(expenses_add=form)


class ExpensesEditHandler(BaseHandler, ItemHandler):
    @protected
    @owner(Expense)
    def GET(self, id):
        form = expenses_edit()
        item = self.current_item()
        form.fill(id=item.id, amount=item.amount, category=item.category,
                note=item.note, date=datetime.strftime(item.date, FORM_DATE_FORMAT))
        return render.expenses_edit_complete(expenses_edit=form)

    @protected
    @owner(Expense)
    def POST(self, id):
        form = expenses_edit()
        if form.validates():
            # Delete old item
            old = self.current_item()
            old.amount = 0
            old.deleted = True
            web.ctx.orm.add(old)

            # Add new one
            e = Expense(user_id=self.current_user().id,
                    amount=float(form.d.amount), category=form.d.category,
                    note=form.d.note,
                    date=datetime.strptime(form.d.date, FORM_DATE_FORMAT))
            web.ctx.orm.add(e)
        return render.expenses_edit(expenses_edit=form)


class ExpensesDeleteHandler(BaseHandler, ItemHandler):
    @protected
    @owner(Expense)
    def POST(self, id):
        e = self.current_item()
        e.amount = 0
        e.deleted = True
        web.ctx.orm.add(e)

        form = expenses_edit()
        return render.expenses_edit(expenses_edit=form)


class ExpensesImportHandler(BaseHandler):
    @protected
    def GET(self):
        return render.expenses_import(user=self.current_user(),
                form=expenses_import())

    @protected
    def POST(self):
        form = expenses_import()
        if not form.validates():
            return render.expenses_import(user=self.current_user(), form=form)

        for line in form.d.expenses.split('\r\n'):
            tokens = line.split('\t')
            date = datetime.strptime(form.d.period + tokens[0],
                    FORM_PERIOD_FORMAT + '%d')
            amount = tokens[2].split()[1]
            note = tokens[3] if len(tokens) >= 4 else ''
            expense = Expense(user_id=self.current_user().id, date=date,
                    category=tokens[1], amount=amount, note=note)
            web.ctx.orm.add(expense)
        web.seeother('/')



if __name__ == '__main__':
    application.run()
