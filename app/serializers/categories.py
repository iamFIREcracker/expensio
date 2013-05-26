#!/usr/bin/env python
# -*- coding: utf-8 -*-


class CategorySerializer(object):

    def __init__(self, category):
        self.o = category

    def to_dict(self):
        return {
            'name': self.o.name,
            'foreground': self.o.foreground,
            'background': self.o.background
        }
