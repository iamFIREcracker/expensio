#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web

from app.forms import categories_edit
from app.models import Category
from app.utils import jsonify
from app.utils import active
from app.utils import owner
from app.utils import protected
from app.utils import BaseHandler


class CategoryWrapper(object):
    __serializable__ = {
            'name': lambda o: o.c.name,
            'foreground': lambda o: o.c.foreground,
            'background': lambda o: o.c.background
            }

    def __init__(self, c):
        self.c = c



class CategoriesHandler(BaseHandler):
    @protected
    def GET(self):
        categories = (web.ctx.orm.query(Category)
                .filter_by(user_id=self.current_user().id)
                .order_by(Category.created.asc())
                .all())
        return jsonify(categories=[CategoryWrapper(c) for c in categories])


class CategoriesEditHandler(BaseHandler):
    @protected
    @owner(Category, 'name')
    @active
    def GET(self, name):
        form = categories_edit()
        item = self.current_item()
        form.fill(name=item.name, foreground=item.foreground,
                  background=item.background)
        return web.ctx.render.categories_edit(categories_edit=form)


    @protected
    @owner(Category, 'name')
    @active
    def POST(self, name):
        form = categories_edit()

        if not form.validates():
            return jsonify(success=False,
                    errors=dict((i.name, i.note) for i in form.inputs
                        if i.note is not None))
        else:
            c = self.current_item()
            c.foreground = form.d.foreground
            c.background = form.d.background
            web.ctx.orm.add(c)
            c = web.ctx.orm.merge(c)
            return jsonify(success=True, user=CategoryWrapper(c))
