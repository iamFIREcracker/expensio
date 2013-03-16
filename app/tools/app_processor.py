#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import web
from web.contrib.template import render_jinja
from webassets.ext.jinja2 import AssetsExtension

import app.config as config
from app.assets import env



def header_html():
    """Global header setter for `text/html` documents."""
    web.header('Content-Type', 'text/html; charset=UTF-8')


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


def load_render(workingdir):
    """Add the renderer to the shared context.

    Inputs:
        workingdir application working directory containing a directory named
        `templates` with all the files to render
    """
    def inner():
        render = render_jinja(os.path.join(workingdir, 'templates'),
                encoding='utf-8', extensions=['jinja2.ext.do',
                                              AssetsExtension])
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

    This hook, other than to set the `orm` variable of the shared context, is in
    charge of execute the handler of the request and catch all the exception:
    if one is raised it will try to commit or rollback the current transaction.

    Inputs:
        dbsession database session
    """
    def inner(handler):
        web.ctx.orm = dbsession

        try:
            res = handler()
        except web.HTTPError:
            web.ctx.orm.commit()
            raise
        except:
            web.ctx.orm.rollback()
            raise
        else:
            web.ctx.orm.commit()
            return res
        finally:
            web.ctx.orm.remove()
    return inner
