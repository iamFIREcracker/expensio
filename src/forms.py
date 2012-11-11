#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from web import form


FORM_DATE_FORMAT = '%Y-%m-%d %H:%M'


validamount = form.Validator(
        '1000.00',
        float)

validdatetime = form.Validator(
        'yyyy-mm-dd hh:mm',
        lambda v: datetime.strptime(v, FORM_DATE_FORMAT))


expenses_add = form.Form(
        form.Textbox('amount', validamount, description='Amount'),
        form.Textbox('category', form.notnull, description='Category',
            id='category'),
        form.Textbox('note', description='Note'),
        form.Textbox('date', validdatetime, description='Date'),
        form.Button('Add', type='submit', class_='right'),
    )

expenses_edit = form.Form(
        form.Hidden('id'),
        form.Textbox('amount', validamount, description='Amount'),
        form.Textbox('category', form.notnull, description='Category',
            id='category'),
        form.Textbox('note', description='Note'),
        form.Textbox('date', validdatetime, description='Date'),
        form.Button('Edit', type='submit', class_='right',
            onclick='ExpensesManager.onEditSubmit(this.form);'),
        form.Button('Delete', type='submit', class_='right',
            onclick='ExpensesManager.onDeleteSubmit(this.form);'),
    )

import_ = form.Form(
        form.Textbox('period', description='Period'),
        form.Textarea('expenses', description='', cols=80, rows=24),
        form.Button('Import', type='sumbit'),
    )
