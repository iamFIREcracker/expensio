#!/usr/bin/env python
# -*- coding: utf-8 -*-


import web


def api(func):
    """Checks that the current request has the header ``HTTP_ACCEPT`` set, and
    that the specified value is actually supported.

    At the moment, the sole content-type supported is ``json``.
    
    If an unsupported content-type is passed then the current request will
    return '406 Not acceptable'."""
    def inner(self, *args, **kwargs):
        accept = web.ctx.environ.get('HTTP_ACCEPT', '').split(',')
        if 'application/json' not in accept:
            raise web.notacceptable()
        return func(self, *args, **kwargs)
    return inner


