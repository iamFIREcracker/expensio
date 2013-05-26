#!/usr/bin/env python
# -*- coding: utf-8 -*-

class UserSerializer(object):

    def __init__(self, user):
        self.o = user

    def to_dict(self):
        return {
            'id': self.o.id,
            'currency': self.o.currency,
        }
