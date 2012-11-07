#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import unicode_literals

import itertools
import json
import operator
import os
import time
import urllib
import urlparse
from datetime import datetime

import web
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import extract
from web.contrib.template import render_jinja

from filters import datetimeformat
from filters import cashformat
from forms import expense
from forms import import_
from forms import loadmore
from models import engine
from models import Expense
from models import User



FACEBOOK_APP_ID = "431016523607887"

FACEBOOK_APP_SECRET = "bcc5a62efaff20fc9808919b3e40a944"


urls = (
    '/', 'MainHandler',
    '/import', 'ImportHandler',
    '/expenses/add', 'ExpensesAdd',
    '/login', 'LoginHandler',
    '/logout', 'LogoutHandler',
    '/periods', 'PeriodsHandler',
)


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


application = web.application(urls, globals())
application.add_processor(load_sqla)
working_dir = os.path.dirname(__file__)
render = render_jinja(os.path.join(working_dir, 'templates'),
        encoding='utf-8', extensions=['jinja2.ext.do'])
render._lookup.filters.update(
        datetime=datetimeformat, cash=cashformat)


def path_url():
    return web.ctx.home + web.ctx.fullpath


def protected(func):
    def inner(self, *args, **kwargs):
        if not self.current_user():
            web.seeother('/')
            return

        return func(self, *args, **kwargs)
    return inner


class BaseHandler():
    def current_user(self):
        """Returns the logged in Facebook user or None."""

        if not hasattr(self, "_current_user"):
            self._current_user = None
            user_id = web.cookies().get('fb_user')
            if user_id:
                self._current_user = (web.ctx.orm.query(User)
                        .filter_by(id=user_id).first())

        return self._current_user


def getcategories(expenses):
    """Given a list of expenses, return the amount spent per category."""
    bycategory = sorted(expenses, key=operator.attrgetter('category'))
    for (category, group) in itertools.groupby(bycategory,
            key=operator.attrgetter('category')):
        yield {'name': category, 'amount':
                sum(map(operator.attrgetter('amount'), group))}


class MainHandler(BaseHandler):
    def GET(self):
        today = datetime.today()
        user_id = self.current_user().id if self.current_user() else ''

        expenses = (web.ctx.orm.query(Expense)
                .filter_by(user_id=user_id)
                .filter(extract('year', Expense.date) == today.year)
                .filter(extract('month', Expense.date) == today.month)
                .order_by(Expense.date.desc()).all())

        categories = sorted(getcategories(expenses),
                key=operator.itemgetter('amount'), reverse=True)

        return render.index(user=self.current_user(), currency='&euro;',
                expenses=expenses, categories=categories, form=expense(),
                more=loadmore())


class ImportHandler(BaseHandler):
    @protected
    def GET(self):
        return render.importexpenses(user=self.current_user(), form=import_())

    @protected
    def POST(self):
        form = import_()
        if not form.validates():
            return render.importexpenses(user=self.current_user(), form=form)

        for line in form.d.expenses.split('\r\n'):
            tokens = line.split('\t')
            date = datetime.strptime(form.d.period + tokens[0], '%Y%m%d')
            amount = tokens[2].split()[1]
            note = tokens[3] if len(tokens) >= 4 else ''
            expense = Expense(user_id=self.current_user().id, date=date,
                    category=tokens[1], amount=amount, note=note)
            web.ctx.orm.add(expense)


class ExpensesAdd(BaseHandler):
    @protected
    def POST(self):
        form = expense()
        if form.validates():
            e = Expense(user_id=self.current_user().id,
                    amount=float(form.d.amount), category=form.d.category,
                    note=form.d.note,
                    date=datetime.strptime(form.d.date, "%d/%m/%Y %I:%M %p"))
            web.debug(e.user_id)
            #web.ctx.orm.add(e)
        return render.expenses_add(form=form)


class UserEditHandler(BaseHandler):

    @protected
    def GET(self):
        pass


class LoginHandler(BaseHandler):
    def GET(self):
        if self.current_user():
            web.seeother('/')
            return

        data = web.input(code=None)
        args = dict(client_id=FACEBOOK_APP_ID, redirect_uri=path_url())
        if data.code is None:
            web.seeother(
                    'http://www.facebook.com/dialog/oauth?' +
                    urllib.urlencode(args))
            return

        args['code'] = data.code
        args['client_secret'] = FACEBOOK_APP_SECRET
        response = urlparse.parse_qs(
                urllib.urlopen(
                    "https://graph.facebook.com/oauth/access_token?" +
                        urllib.urlencode(args)).read())
        access_token = response["access_token"][-1]
        profile = json.load(
                urllib.urlopen(
                    "https://graph.facebook.com/me?" +
                    urllib.urlencode(dict(access_token=access_token))))

        user = User(id=str(profile["id"]), name=profile["name"],
                access_token=access_token)
        user = web.ctx.orm.merge(user) # Merge flying and persistence object
        web.ctx.orm.add(user)

        web.setcookie(
                'fb_user', str(profile['id']), expires=time.time() + 7 * 86400)
        return web.seeother('/')


class LogoutHandler():
    def GET(self):
        web.setcookie('fb_user', '', expires=time.time() - 86400)
        web.seeother('/')


if __name__ == '__main__':
    application.run()
