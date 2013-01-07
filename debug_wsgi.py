#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from werkzeug.debug import DebuggedApplication
from app import app


def nointernalerror():
    raise sys.exc_info()
app.internalerror = nointernalerror


app = DebuggedApplication(app.wsgifunc(), evalex=True)
