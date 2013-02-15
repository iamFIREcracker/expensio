#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import uuid

import web


class UploadedFile(object):

    def __init__(self, name):
        defaults = {name:{}}
        data = web.input(**defaults)
        self.delegate = getattr(data, name)

    def __nonzero__(self):
        return self.delegate != ''

    @property
    def filename(self):
        return self.delegate.filename

    @property
    def file(self):
        return self.delegate.file


class UploadManager(object):

    def __init__(self, ddir, wdir):
        self._ddir = ddir
        self._wdir = wdir

    def add(self, uploaded):
        _, extension = os.path.splitext(uploaded.filename)

        filename = '{0}{1}'.format(uuid.uuid4(), extension)
        relativepath = os.path.join(self._ddir, filename)
        absolutepath = os.path.join(self._wdir, relativepath)

        with open(absolutepath, 'wb') as f:
            f.write(uploaded.file.read())

        return os.path.join(web.ctx.home, relativepath)
