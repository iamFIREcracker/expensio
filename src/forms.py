#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime

from web import form

import parsers


FORM_PERIOD_FORMAT = '%Y-%m'


validcurrency = form.Validator(
        '€, $ ..',
        lambda v: v in ['€', '$'])

validamount = form.Validator('1000.00', parsers.amount)

validdatetime = form.Validator('yyyy-mm-dd', parsers.date)


users_edit = form.Form(
        form.Hidden('id'),
        form.Textbox('name', form.notnull, description='Name'),
        form.Textbox('currency', validcurrency, description='Currency'),
        form.Button('google_connect', html='Google Connect'),
        form.Button('facebook_connect', html='Facebook Connect'),
        form.Button('twitter_connect', html='Twitter Connect'),
        form.Button('Edit', type='submit',
            onclick='UsersManager.onEditSubmit(this.form);'),
    )


expenses_add = form.Form(
        form.Textbox('amount', validamount, description='Amount'),
        form.Textbox('category', form.notnull, description='Category',
            id='category'),
        form.Textbox('note', description='Note'),
        form.Textbox('date', validdatetime, description='Date'),
        form.Button('Add', type='submit'),
    )

expenses_edit = form.Form(
        form.Hidden('id'),
        form.Textbox('amount', validamount, description='Amount'),
        form.Textbox('category', form.notnull, description='Category',
            id='category'),
        form.Textbox('note', description='Note'),
        form.Textbox('date', validdatetime, description='Date'),
        form.Button('Edit', type='submit',
            onclick='ExpensesManager.onEditSubmit(this.form);'),
        form.Button('Delete', type='submit',
            onclick='ExpensesManager.onDeleteSubmit(this.form);'),
    )


validperiod = form.Validator(
        'yyyy-mm',
        lambda v: datetime.strptime(v, FORM_PERIOD_FORMAT))

def fetch_expenses(form):
    period = form.period
    data = form.data
    expenses = []

    for line in data.split('\r\n'):
        (date_, category_, amount_, note_) = line.split('\t')

        expenses.append((
            datetime.strptime(period + date_, FORM_PERIOD_FORMAT + '%d'),
            category_, parsers.amount(amount_), note_,))
    return expenses


validimportdata = form.Validator(
        '2012-11-12	dinner	25	Dinner with parents', fetch_expenses)


expenses_import = form.Form(
        form.Textbox('period', validperiod, description='Period'),
        form.Textarea('data', form.notnull, description='Data', cols=80,
            rows=24),
        form.Button('Import', type='sumbit',
            onclick='ExpensesManager.onImportSubmit(this.form);'),
        validators=[validimportdata]
    )
