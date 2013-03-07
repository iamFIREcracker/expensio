#!/usr/bin/env python
# -*- coding: utf-8 -*-

from webassets import Bundle
from webassets import Environment

import app.config as config

env = Environment('./static', '/static')
env.debug = config.DEBUG
env.register('base_css', Bundle("bootstrap/css/bootstrap.min.css",
                                "bootstrap/css/bootstrap-responsive.min.css",
                                "bootstrap-datepicker/css/datepicker.css",
                                "bootstrap-fileupload/css/bootstrap-fileupload.min.css",
                                "css/main.css"))

env.register('base_js', Bundle("jquery-form/jquery.form.js",
                               "bootstrap/js/bootstrap.min.js",
                               "bootstrap-datepicker/js/bootstrap-datepicker.js",
                               "underscore/js/underscore.min.js",
                               "js/sprintf.js",
                               "js/common.js",
                               "js/logger.js",
                               "js/formatter.js",
                               "js/palette.manager.js",
                               "js/expenses.ui.js",
                               "js/expenses.manager.js"))

env.register('users_js', Bundle("js/users.ui.js",
                                "js/users.manager.js"))

env.register('categories_js', Bundle("js/categories.ui.js",
                                     "js/categories.manager.js"))

env.register('days_js', Bundle("js/days.ui.js",
                               "js/days.manager.js"))
