#!/usr/bin/env python
# -*- coding: utf-8 -*-



class LoggingSubscriber(object):
    """A generic subscriber in charge of logging each received event.

    >>> from collections import namedtuple
    >>> Logger = namedtuple('Logger', 'info'.split())
    >>> def info(message):
    ...   print message
    >>> logger = Logger(info)
    >>> this = LoggingSubscriber(logger)

    >>> this.on_button_clicked('Button1')
    Received event='on_button_clicked' args=('Button1',)

    >>> this.on_validation_error('Invalid format')
    Received event='on_validation_error' args=('Invalid format',)
    """
    def __init__(self, logger):
        self.logger = logger

    def __getattr__(self, name):
        def callable(*args):
            msg = 'Received event=%(event)r args=%(args)r'
            msg = msg % dict(event=name, args=args)
            self.logger.info(msg)
        return callable




