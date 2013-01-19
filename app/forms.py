#!/usr/bin/env python
# -*- coding: utf-8 -*-

from web import form

import parsers
import utils

class Image(form.Input):
    """Image.
    
    >>> Image("foo").render()
    u'<img id="foo" name="foo" />'
    >>> Image("foo", src="bar", alt="baz").render()
    u'<img src="bar" alt="baz" id="foo" name="foo" />'
    """
    def __init__(self, name, *validators, **attrs):
        super(Image, self).__init__(name, *validators, **attrs)

    def render(self):
        attrs = self.attrs.copy()
        attrs['name'] = self.name
        if self.value is not None:
            attrs['src'] = self.value
        if self.value is not None:
            attrs['value'] = self.value
        return '<img %s />' % (attrs, )


validcurrency = form.Validator('€, $ ..', parsers.currency)
validamount = form.Validator('1000.00', parsers.amount)
validdate = form.Validator('mm/dd/yyyy', parsers.date_us)
validimportdata = form.Validator('Invalid format', parsers.expenses)


users_edit = form.Form(
        form.Hidden('id'),
        form.Textbox('name', form.notnull, description='Name'),
        form.Dropdown('currency', zip(utils.currencies(), utils.currencies()),
            description='Currency'),
        #form.Button('google_connect', html='Google Connect'),
        #form.Button('facebook_connect', html='Facebook Connect'),
        #form.Button('twitter_connect', html='Twitter Connect'),
        form.Button('Done', type='submit', class_="btn btn-primary",
            onclick='UsersManager.onEditSubmit(this.form);'),
    )


expenses_add = form.Form(
        form.Textbox('amount', validamount, description='Amount'),
        form.Textbox('category', form.notnull, description='Category',
            id='category'),
        form.Textbox('note', description='Note'),
        form.Textbox('date', validdate, description='Date'),
        form.File('attachment', description='Attachment'),
        form.Button('Add', type='submit', class_="btn btn-primary"),
    )

expenses_edit = form.Form(
        form.Hidden('id'),
        form.Textbox('amount', validamount, description='Amount'),
        form.Textbox('category', form.notnull, description='Category',
            id='category'),
        form.Textbox('note', description='Note'),
        form.Textbox('date', validdate, description='Date'),
        form.File('attachment', description='Attachment'),
        Image('oldattachment', description='Old Attachment', width="200px"),
        form.Button('Done', type='submit', class_="btn btn-primary"),
    )

expenses_import = form.Form(
        form.Textarea('data', validimportdata, description='', rows=24),
        form.Button('Import', type='sumbit', class_="btn btn-primary")
    )


if __name__ == "__main__":
    import doctest
    doctest.testmod()
