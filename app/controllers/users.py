#!/usr/bin/env python
# -*- coding: utf-8 -*-

import celery
import web

import app.tasks as tasks
from app.forms import users_avatar
from app.forms import users_edit
from app.forms import users_delete
from app.upload import UploadedFile
from app.utils import jsonify
from app.utils import logout
from app.utils import me
from app.utils import protected
from app.utils import BaseHandler

class UserWrapper(object):
    __serializable__ = {
            'id': lambda o: o.u.id,
            'currency': lambda o: o.u.currency,
            }

    def __init__(self, u):
        self.u = u


class UsersAvatarUploadChange(BaseHandler):

    @protected
    @me
    def POST(self, id):
        avatar = UploadedFile('avatar')
        form = users_avatar()

        if not form.validates():
            return jsonify(success=False,
                    errors=dict((i.name, i.note) for i in form.inputs
                        if i.note is not None))
        else:
            task_id = tasks.UsersAvatarChangeTask.delay(
                    avatar, web.ctx.exportman, self.current_user()).task_id
            return jsonify(success=True,
                    goto='/users/avatar/change/status/%s' % task_id)


class UsersAvatarUploadChangeStatusHandler(BaseHandler):

    @protected
    def GET(self, task_id):
        try:
            retval = (tasks.UsersAvatarUploadTask.AsyncResult(task_id)
                    .get(timeout=1.0))
        except celery.exceptions.TimeoutError:
            return jsonify(success=False, goto=web.ctx.path)
        else:
            return jsonify(success=True, goto=retval)


class UsersAvatarUploadRemove(BaseHandler):
    @protected
    @me
    def POST(self, id):
        u = self.current_user()
        u.avatar = None
        web.ctx.orm.add(u)
        u = web.ctx.orm.merge(u)
        return jsonify(success=True, user=UserWrapper(u))


class UsersEditHandler(BaseHandler):
    @protected
    @me
    def GET(self, id):
        form = users_edit()
        user = self.current_user()
        form.fill(id=user.id, name=user.name, currency=user.currency)
        return web.ctx.render.users_edit_complete(user=self.current_user(),
                users_edit=form)

    @protected
    @me
    def POST(self, id):
        form = users_edit()
        if not form.validates():
            return jsonify(success=False,
                    errors=dict((i.name, i.note) for i in form.inputs
                        if i.note is not None))
        else:
            u = self.current_user()
            u.name = form.d.name
            u.currency = form.d.currency
            web.ctx.orm.add(u)
            u = web.ctx.orm.merge(u)
            return jsonify(success=True, user=UserWrapper(u))


class UsersDeleteHandler(BaseHandler):
    @protected
    @me
    def GET(self, id):
        form = users_delete()
        user = self.current_user()
        form.fill(id=user.id)
        return web.ctx.render.users_delete_complete(user=self.current_user(),
                users_delete=form)

    @protected
    @me
    def POST(self, id):
        u = self.current_user()
        u.deleted = True
        web.ctx.orm.add(u)
        logout()
        return jsonify(success=True)
