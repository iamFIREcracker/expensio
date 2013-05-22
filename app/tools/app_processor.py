#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
from web.contrib.template import render_jinja
from webassets.ext.jinja2 import AssetsExtension

import app.config as config
import app.exceptions
from app.assets import env



def header_json():
    """Global header setter for `text/json` documents."""
    web.header('Content-Type', 'text/json; charset=UTF-8')


def notfound():
    """Customized 404 Not Found message."""
    web.ctx.status = '404 Not Found'
    return web.notfound(web.ctx.render._404())


def internalerror():
    """Customized 500 Internal Server Error message."""
    web.ctx.status = '500 Internal Server Error'
    return web.internalerror(web.ctx.render._500())


def load_path_url():
    """Add path_url property to the shared context."""
    web.ctx.path_url = web.ctx.home + web.ctx.path


def load_logger(logger):
    """Add a logger to the shared context.

    Inputs:
        logger logger instance
    """
    def inner():
        web.ctx.logger = logger
    return inner


def load_render(views):
    """Add the renderer to the shared context.

    Inputs:
        views path containing application views
    """
    def inner():
        render = render_jinja(
                views, encoding='utf-8',
                extensions=['jinja2.ext.do', AssetsExtension])
        render._lookup.assets_environment = env
        render._lookup.globals.update({'DEV': config.DEV})
        web.ctx.render = render;
    return inner


def load_session(session):
    """Load the session into the shared context.
    
    Inputs:
        session object keeping track of sessions
    """
    def inner():
        web.ctx.session = session
    return inner


def load_keyvalue(key, value):
    """Load the upload manager into the shared context.

    Inputs:
        key name of the object to add into the shared context
        value object to add into the shared object
    """
    def inner():
        setattr(web.ctx, key, value)
    return inner


def load_sqla(dbsession):
    """Load SQLAlchemy database session and manage exceptions properly.

    Inputs:
        dbsession database session
    """
    def inner(handler):
        web.ctx.orm = dbsession()

        try:
            return handler()
        finally:
            dbsession.remove()
    return inner


def manage_content_exceptions(handler):
    """Checks if ``ResponseContent`` exceptions are thrown by the request
    handler, and in that case, return the wrapped content.

    >>> def handler():
    ...   print 'Hello, world!'
    >>> manage_content_exceptions(handler)
    Hello, world!

    >>> def handler():
    ...   raise app.exceptions.ResponseContent('Hello, exception!')
    >>> manage_content_exceptions(handler)
    'Hello, exception!'
    """
    try:
        return handler()
    except app.exceptions.ResponseContent as r:
        return r.content
