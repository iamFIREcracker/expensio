#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import uuid

import web

from config import UPLOAD_DIR


class UploadManager(object):

    def __init__(self, wdir):
        self._wdir = wdir

    def add(self, uploaded):
        _, extension = os.path.splitext(uploaded.filename)

        filename = '{0}{1}'.format(uuid.uuid4(), extension)
        relativepath = os.path.join(UPLOAD_DIR, filename)
        absolutepath = os.path.join(self._wdir, relativepath)

        with open(absolutepath, 'wb') as f:
            f.write(uploaded.file.read())

        return os.path.join(web.ctx.home, relativepath)
