#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import tee

import web
from web import form

from app import config
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
        if self.value is not None:
            attrs['src'] = self.value

        return """
<img src='{src}' class='img-rounded pull-left' width='{width}' height='{height}'>
<div class="btn-group" style="margin-left: 20px">
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


class Connect(form.Input):
    def __init__(self, name, *validators, **attrs):
        self.connected = False
        description = attrs.pop('description', name)
        super(Connect, self).__init__(name, *validators, **attrs)
        self.description = description

    def render(self):
        attrs = self.attrs.copy()
        if self.connected:
            value = 'Disconnect'
            attrs['href'] = '/accounts/%s/disconnect' % self.id
            attrs['title'] = 'Disconnect from %s' % self.description
        else:
            value = 'Connect'
            attrs['href'] = '/login/%s?back=%s' % (self.id, web.ctx.path)
            attrs['title'] = 'Connect to %s' % self.description
        return '<a %s>%s</a>' % (attrs, value)

    def set_value(self, value):
        self.connected = bool(value)

    def get_value(self):
        return self.connected


class Colopicker(form.Textbox):
    def render(self):
        return """
<div class="input-append color" data-color="%(value)s">
    %(input)s
    <span class="add-on"><i style="background-color: %(value)s;"></i></span>
</div>
""" % dict(value=self.value, input=super(Colopicker, self).render())


class DevelopmentForm(form.Form):
    def __init__(self, *inputs, **kw):
        filtered = filter(lambda i: 'DEV' not in i.attrs or config.DEV,
                          inputs)
        super(DevelopmentForm, self).__init__(*filtered, **kw)


validaccounts = form.Validator(
        "There should be - at least - one external account linked!",
        lambda i: any(v for v in i.itervalues()))
validcurrency = form.Validator('€, $ ..', parsers.currency)
validformat = form.Validator('tsv, csv ..', parsers.format)
validamount = form.Validator('Invalid (e.g. 1.00)', parsers.amount)
validdate = form.Validator('Invalid (e.g. 1/22/2013)', parsers.date_us)
validimportdata = form.Validator('Invalid format', parsers.expenses)
validcolor = form.Validator('Invalid color (e.g. #1234ab)', parsers.color)


users_avatar = form.Form(
        form.Hidden('id'),
        ImageBootstrap2('avatar', form.notnull, width=config.AVATAR_WIDTH,
            height=config.AVATAR_HEIGHT, src=config.AVATAR_PLACEHOLD,
            description='Avatar'),
    )

users_edit = form.Form(
        form.Hidden('id'),
        form.Textbox('name', form.notnull, description='Name',
            placeholder="John Smith"),
        form.Dropdown('currency', zip(*tee([''] + utils.currencies())),
            validcurrency, description='Currency'),
    )

users_connect = DevelopmentForm(
        Connect('google', description='Google',
            class_='btn-connect btn-connect-google'),
        Connect('facebook', description='Facebook',
            class_='btn-connect btn-connect-facebook'),
        Connect('twitter', description='Twitter',
            class_='btn-connect btn-connect-twitter'),
        Connect('fake', description='Fake',
            class_='btn-connect', DEV=True),
        validators=[validaccounts]
    )


users_delete = form.Form(
        form.Hidden('id'),
    )


expenses_add = form.Form(
        form.Textbox('date', validdate, description='Date', placeholder='1/22/2013'),
        form.Textbox('category', form.notnull, description='Category', placeholder='bar'),
        form.Textbox('note', description='Note', placeholder='coffe with mom'),
        form.Textbox('amount', validamount, description='Amount', placeholder='1.00'),
        FileBootstrap('attachment', description='Attachment'),
    )

expenses_edit = form.Form(
        form.Hidden('id'),
        form.Textbox('date', validdate, description='Date'),
        form.Textbox('category', form.notnull, description='Category',
            id='category'),
        form.Textbox('note', description='Note'),
        form.Textbox('amount', validamount, description='Amount'),
        FileBootstrap('attachment', description='Attachment'),
    )

expenses_export = form.Form(
        form.Dropdown('Format', zip(utils.formats(), utils.formats()),
            validformat, description='Format'),
    )

expenses_import = form.Form(
        form.Textarea('data', validimportdata, description='',
            class_="span12", rows=24,
            placeholder="1/22/2013	bar	1.00	coffe with mom")
    )


categories_edit = form.Form(
        form.Hidden('name'),
        Colopicker('foreground', validcolor, description='Foreground',
                class_="input-small", readonly=""),
        Colopicker('background', validcolor, description='Background',
                class_="input-small", readonly=""),
    )
