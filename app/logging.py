#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
flask.logging
~~~~~~~~~~~~~

Implements the logging support for Flask.

:copyright: (c) 2011 by Armin Ronacher.
:license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import

from logging import getLogger, StreamHandler, Formatter, DEBUG


def create_logger(config):
    """Creates a logger for the given application.  Furthermore this function
    also removes all attached handlers in case there was a logger with the log
    name before.
    """
    class DebugHandler(StreamHandler):
        def emit(x, record):
            StreamHandler.emit(x, record) if config.debug else None

    handler = DebugHandler()
    handler.setLevel(DEBUG)
    handler.setFormatter(Formatter(config.log_format))
    logger = getLogger(config.logger_name)
    # just in case that was not a new logger, get rid of all the handlers
    # already attached to it.
    del logger.handlers[:]
    logger.addHandler(handler)
    return logger
