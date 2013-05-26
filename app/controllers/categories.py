#!/usr/bin/env python
# -*- coding: utf-8 -*-

import celery
import web

import app.tasks as tasks
from app.forms import categories_edit
from app.models import Category
from app.serializers import CategorySerializer
from app.utils import jsonify
from app.utils import active
from app.utils import owner
from app.utils import protected
from app.utils import BaseHandler


class CategoriesHandler(BaseHandler):
    @protected
    def GET(self):
        categories = (web.ctx.orm.query(Category)
                .filter_by(user_id=self.current_user().id)
                .order_by(Category.created.asc())
                .all())
        return jsonify(categories=[CategorySerializer(c) for c in categories])


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
            web.ctx.orm.commit()
            c = web.ctx.orm.merge(c)
            return jsonify(success=True, user=CategorySerializer(c))


class CategoriesResetHandler(BaseHandler):
    @protected
    def POST(self):
        task_id = tasks.CategoriesResetTask.delay(self.current_user()).task_id
        return jsonify(success=True,
                goto='/categories/reset/status/%s' % task_id)


class CategoriesResetStatusHandler(BaseHandler):
    @protected
    def GET(self, task_id):
        try:
            retval = (tasks.CategoriesResetTask.AsyncResult(task_id)
                    .get(timeout=1.0))
        except celery.exceptions.TimeoutError:
            return jsonify(success=False, goto=web.ctx.path)
        else:
            return jsonify(success=True,
                    goto=[CategorySerializer(c) for c in retval])
