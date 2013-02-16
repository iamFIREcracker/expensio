#!/usr/bin/env python
# -*- coding: utf-8 -*-

from web import form

import parsers
import utils


class ImageBootstrap(form.Input):
    def render(self):
        attrs = self.attrs.copy()
        attrs['name'] = self.name
        attrs['src'] = "http://www.placehold.it/210x150/EFEFEF/AAAAAA&text=no+image"
        attrs['class'] = "img-rounded"
        attrs['width'] = 220
        attrs['height'] = 150
        if self.value is not None:
            attrs['src'] = self.value
        return '<img %s />' % (attrs, )


class ImageBootstrap2(form.Input):
    def render(self):
        attrs = self.attrs.copy()
        if 'width' not in attrs:
            attrs['width'] = 72
        if 'height' not in attrs:
            attrs['height'] = 72
        attrs['src'] = "http://www.placehold.it/{width}x{height}/EFEFEF/AAAAAA&text=no+image".format(**attrs)
        if self.value is not None:
            attrs['src'] = self.value

        return """
<img src='{src}' class='img-rounded pull-left' width='{width}' height='{height}'>
<div class="btn-group span1">
    <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
        Change
        <span class="caret"></span>
    </a>
    <ul class="dropdown-menu">
        <li>
            <a id="choose">Choose another</a>
        </li>
        <li>
            <a id="remove">Remove</a>
        </li>
    </ul>
</div>
""".format(**attrs)


class FileBootstrap(form.File):
    def render(self):
        return """
<div class="fileupload fileupload-new" data-provides="fileupload">
  <div class="input-append">
    <div class="uneditable-input"><i class="icon-file fileupload-exists"></i> <span class="fileupload-preview"></span></div><span class="btn btn-file"><span class="fileupload-new">Select file</span><span class="fileupload-exists">Change</span>%s</span>
  </div>
</div>
""" % super(FileBootstrap, self).render()



validcurrency = form.Validator('€, $ ..', parsers.currency)
validformat = form.Validator('tsv, csv ..', parsers.format)
validamount = form.Validator('Invalid (e.g. 1.00)', parsers.amount)
validdate = form.Validator('Invalid (e.g. 1/22/2013)', parsers.date_us)
validimportdata = form.Validator('Invalid format', parsers.expenses)


users_avatar = form.Form(
        form.Hidden('id'),
        ImageBootstrap2('avatar', form.notnull, description='Avatar'),
    )

users_edit = form.Form(
        form.Hidden('id'),
        form.Textbox('name', form.notnull, description='Name',
            placeholder="John Smith"),
        form.Dropdown('currency', zip(utils.currencies(), utils.currencies()),
            validcurrency, description='Currency'),
    )


users_delete = form.Form(
        form.Hidden('id'),
    )


expenses_add = form.Form(
        form.Textbox('amount', validamount, description='Amount', placeholder='1.00'),
        form.Textbox('category', form.notnull, description='Category', placeholder='bar'),
        form.Textbox('note', description='Note', placeholder='coffe with mom'),
        form.Textbox('date', validdate, description='Date', placeholder='1/22/2013'),
        FileBootstrap('attachment', description='Attachment'),
    )

expenses_edit = form.Form(
        form.Hidden('id'),
        form.Textbox('amount', validamount, description='Amount'),
        form.Textbox('category', form.notnull, description='Category',
            id='category'),
        form.Textbox('note', description='Note'),
        form.Textbox('date', validdate, description='Date'),
        FileBootstrap('attachment', description='Attachment'),
        ImageBootstrap('oldattachment', description='Old Attachment'),
    )

expenses_export = form.Form(
        form.Dropdown('Format', zip(utils.formats(), utils.formats()),
            validformat, description='Format'),
    )

expenses_import = form.Form(
        form.Textarea('data', validimportdata, description='',
            class_="span6", rows=24,
            placeholder="1/22/2013	bar	1.00	coffe with mom")
    )
