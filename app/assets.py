#!/usr/bin/env python
# -*- coding: utf-8 -*-

from webassets import Environment

import app.config as config

env = Environment('./static', '/static')
env.debug = config.DEBUG
