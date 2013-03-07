#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from werkzeug.debug import DebuggedApplication

import app.app as app
import app.config as config


if config.DEBUG:
    def nointernalerror():
        raise sys.exc_info()
    app.internalerror = nointernalerror

    app = DebuggedApplication(app.wsgifunc(), evalex=True)
else:
    app = app.wsgifunc()
