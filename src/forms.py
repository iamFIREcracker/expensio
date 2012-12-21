#!/usr/bin/env python
# -*- coding: utf-8 -*-

from web import form

import parsers


validcurrency = form.Validator('€, $ ..', parsers.currency)
validamount = form.Validator('1000.00', parsers.amount)
validdate = form.Validator('yyyy-mm-dd', parsers.date)
validperiod = form.Validator('yyyy-mm', parsers.period)
validimportdata = form.Validator(
        '2012-11-12	dinner	25	Dinner with parents',
        lambda f: parsers.expenses(f.period, f.data))


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
        form.Textbox('date', validdate, description='Date'),
        form.Button('Add', type='submit'),
    )

expenses_edit = form.Form(
        form.Hidden('id'),
        form.Textbox('amount', validamount, description='Amount'),
        form.Textbox('category', form.notnull, description='Category',
            id='category'),
        form.Textbox('note', description='Note'),
        form.Textbox('date', validdate, description='Date'),
        form.File('attachment', description='Attachment'),
        form.Button('Edit', type='submit'),
    )

expenses_import = form.Form(
        form.Textbox('period', validperiod, description='Period'),
        form.Textarea('data', form.notnull, description='Data', cols=80,
            rows=24),
        form.Button('Import', type='sumbit',
            onclick='ExpensesManager.onImportSubmit(this.form);'),
        validators=[validimportdata]
    )
