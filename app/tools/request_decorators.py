#!/usr/bin/env python
# -*- coding: utf-8 -*-


import web


def html(func):
    """Sets the 'Content-type' header to 'text/html'.

    >>> class Headers(list):
    ...   def append(self, v):
    ...     print v
    >>> request = lambda: None

    >>> web.ctx['headers'] = Headers()
    >>> html(request)()
    ('Content-Type', 'text/html; charset=UTF-8')
    """
    def inner(*args, **kwargs):
        web.header('Content-Type', 'text/html; charset=UTF-8')
        return func(*args, **kwargs)
    return inner


def api(func):
    """Checks that the current request has the header ``HTTP_ACCEPT`` set, and
    that the specified value is actually supported by the server.

    If an unsupported content-type is passed a ``web.notacceptable`` exception
    is raised and the status '406 Not acceptable' is sent back to the client.


    >>> class MyNotAcceptable(Exception):
    ...   pass
    >>> web.notacceptable = MyNotAcceptable
    >>> request = lambda: 'Hello world'


    >>> web.ctx['environ'] = dict()
    >>> api(request)()
    Traceback (most recent call last):
        ...
    MyNotAcceptable


    >>> web.ctx['environ'] = dict(HTTP_ACCEPT='application/xml')
    >>> api(request)()
    Traceback (most recent call last):
        ...
    MyNotAcceptable

    >>> web.ctx['environ'] = dict(HTTP_ACCEPT='application/json')
    >>> api(request)()
    'Hello world'
    """
    def inner(*args, **kwargs):
        accept = web.ctx.environ.get('HTTP_ACCEPT', '').split(',')
        if 'application/json' not in accept:
            raise web.notacceptable()
        return func(*args, **kwargs)
    return inner



if __name__ == '__main__':
    import doctest
    doctest.testmod()
