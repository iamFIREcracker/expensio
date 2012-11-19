#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import web

from models import AlchemyEncoder # XXX WTF?


def jsonify(*args, **kwargs):
    web.header('Content-Type', 'application/json')

    return json.dumps(dict(*args, **kwargs), cls=AlchemyEncoder)
