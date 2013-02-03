#!/usr/bin/env python
# -*- coding: utf-8 -*-

import app.formatters as formatters
from app.celery import celery
from app.database import db_session
from app.models import Expense

class ExpenseTSVWrapper(object):

    def __init__(self, e):
        self.e = e

    def __repr__(self):
        date = formatters.date_us(self.e.date)
        category = self.e.category
        amount = "{:,.2f}".format(self.e.amount)
        note = self.e.note

        return '%s\n' % ('\t'.join([date, category, amount, note]), )


@celery.task
def ExpensesExportTSVTask(exportman, user):
    filename = 'expenses.tsv'
    expenses = (db_session.query(Expense)
                .filter_by(user_id=user.id)
                .filter(Expense.deleted == False)
                .order_by(Expense.date.desc())
                .all())
    return exportman.add(user.id, filename,
            (ExpenseTSVWrapper(e) for e in expenses))
