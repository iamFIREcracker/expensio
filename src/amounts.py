#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta

import web
from sqlalchemy import func

from config import LATEST_DAYS_DATE_FORMAT
from config import DATE_FORMAT
from config import EPOCH
from formatters import dateformatter
from handlers import protected
from handlers import BaseHandler
from models import Expense
from utils import jsonify



SECONDS_TO_DAYS = 60 * 60 * 24


class Day(object):
    __serializable__ = {
            'date': lambda o: o.d[0],
            'updated': lambda o: dateformatter(o.d[1]),
            'delta': lambda o: int(o.d[2]),
            'amount': lambda o: o.d[3],
            'currency': lambda o: o.currency,
            }

    def __init__(self, day, currency):
        self.d = day
        self.currency = currency



class AmountsHandler(BaseHandler):
    @protected
    def GET(self):
        today = datetime.today()
        data = web.input(days=30, latest=None)
        user_id = self.current_user().id

        days = int(data.days)
        latest = datetime.strptime(
                data.latest if data.latest else EPOCH, DATE_FORMAT)

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
