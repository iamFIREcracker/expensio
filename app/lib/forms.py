#!/usr/lib/env python
# -*- coding: utf-8 -*-


from app.lib.pubsub import Publisher


class FormValidator(Publisher):
    """
    >>> class Form(object):
    ...   def __init__(self, validates):
    ...     self.validates = validates
    >>> class Subscriber(object):
    ...   def invalid_form(self, error):
    ...     print 'Invalid: %(reason)s' % dict(reason=error)
    ...   def valid_form(self, *args):
    ...     print 'Valid!'
    >>> this = FormValidator()
    >>> this.add_subscriber(Subscriber())

    >>> this.perform(Form(lambda: False), lambda f: None)
    Invalid: None
    >>> this.perform(Form(lambda: False), lambda f: 'currency')
    Invalid: currency

    >>> this.perform(Form(lambda: True), lambda f: 'currency')
    Valid!
    """

    def perform(self, form, invalidformdescriber):
        """Validates ``form`` and publish result messages accordingly.

        On success a 'valid_form' message is published with the form just
        validated.  On the other hand, if something went wrong during the
        validaiton, an 'invalid_form' message is published, together with the
        reason of the invalidation.
        """
        if form.validates():
            self.publish('valid_form', form)
        else:
            self.publish('invalid_form', invalidformdescriber(form))
