#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import uuid

import web


class UploadedFile(object):

    def __init__(self, name):
        defaults = {name:{}}
        data = web.input(**defaults)
        f = getattr(data, name)

        if f != '':
            with tempfile.NamedTemporaryFile("w+b", delete=False) as tmp:
                tmp.write(f.file.read())

                self.filename = f.filename
                self.name = tmp.name

    def __nonzero__(self):
        return hasattr(self, 'filename')



class UploadManager(object):

    def __init__(self, ddir, wdir):
        self._ddir = ddir
        self._wdir = wdir

    def add(self, uploaded):
        _, extension = os.path.splitext(uploaded.filename)

        filename = '{0}{1}'.format(uuid.uuid4(), extension)
        relativepath = os.path.join(self._ddir, filename)
        absolutepath = os.path.join(self._wdir, relativepath)

        with open(absolutepath, 'wb') as fout:
            with open(uploaded.name, 'rb') as fin:
                fout.write(fin.read())

        os.unlink(uploaded.name)
        return relativepath
