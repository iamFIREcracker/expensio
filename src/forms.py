#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from web import form


validamount = form.Validator(
        '1000.00',
        float)

validdatetime = form.Validator(
        'dd/mm/yyyy hh:mm AM',
        lambda v: datetime.strptime(v, "%d/%m/%Y %I:%M %p"))

expense = form.Form(
        form.Textbox('amount', validamount, description='Amount'),
        form.Textbox('category', form.notnull, description='Category', id='category'),
        form.Textbox('note', description='Note'),
        form.Textbox('date', validdatetime, description='Date'),
    )

import_ = form.Form(
        form.Textbox('period', description='Period'),
        form.Textarea('expenses', description='', cols=80, rows=24),
        form.Button('Import', type='sumbit')
    )

loadmore = form.Form(
        form.Button("Load more", type="submit", id="more")
    )
