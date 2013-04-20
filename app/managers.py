#!/usr/bin/env python
# -*- coding: utf-8 -*-

import app.config as config
from app.models import Category



class Categories(object):
    
    @staticmethod
    def exists(category_name, user_id):
        """Returns True if a category with name ``category_name`` and
        associated with the user ID ``user_id`` is already present in the
        system, False otherwise.
        """
        c = (Category.query
                .filter_by(user_id=user_id)
                .filter_by(name=category_name)
                .first())
        return c is not None

    @staticmethod
    def new(category_name, user_id):
        """Creates a new category with name ``category_name`` and associated
        with the user ID ``user_id``.
        """
        return Category(
                user_id=user_id, name=category_name,
                foreground=config.CATEGORY_FOREGROUND,
                background=config.CATEGORY_BACKGROUND)
