#!/usr/bin/env python
# -*- coding: utf-8 -*-

from web import form

expense = form.Form(
        form.Textbox('category', description='Category', id='category'),
        form.Textbox('amount', form.notnull, description='Amount'),
        form.Textbox('comment', description='Comment'),
        form.Button('Add', type='Submit', id='add')
    )

import_ = form.Form(
        form.Textbox('period', description='Period'),
        form.Textarea('expenses', description='', cols=80, rows=24),
        form.Button('Import', type='Sumbit')
    )

loadmore = form.Form(
        form.Button("Load more", type="Submit", id="more")
    )

