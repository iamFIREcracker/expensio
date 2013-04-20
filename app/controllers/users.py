#!/usr/bin/env python
# -*- coding: utf-8 -*-

import celery
import web

import app.tasks as tasks
from app.forms import users_avatar
from app.forms import users_edit
from app.serializers import UserSerializer
from app.upload import UploadedFile
from app.utils import jsonify
from app.utils import logout
from app.utils import me
from app.utils import protected
from app.utils import BaseHandler



class UsersAvatarChange(BaseHandler):

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
                    avatar, web.ctx.avatarman, self.current_user(), web.ctx.home).task_id
            return jsonify(success=True,
                    goto='/users/%s/avatar/change/status/%s' % (
                            self.current_user().id, task_id))


class UsersAvatarChangeStatusHandler(BaseHandler):
    @protected
    @me
    def GET(self, id, task_id):
        try:
            retval = (tasks.UsersAvatarChangeTask.AsyncResult(task_id)
                    .get(timeout=1.0))
        except celery.exceptions.TimeoutError:
            return jsonify(success=False, goto=web.ctx.path)
        else:
            return jsonify(success=True, avatar=retval)


class UsersAvatarRemove(BaseHandler):
    @protected
    @me
    def POST(self, id):
        u = self.current_user()
        u.avatar = None
        web.ctx.orm.add(u)
        web.ctx.orm.commit()
        u = web.ctx.orm.merge(u)
        return jsonify(success=True, user=UserSerializer(u))


class UsersEditHandler(BaseHandler):
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
            web.ctx.orm.commit()
            u = web.ctx.orm.merge(u)
            return jsonify(success=True, user=UserSerializer(u))


class UsersDeleteHandler(BaseHandler):
    @protected
    @me
    def POST(self, id):
        u = self.current_user()
        u.deleted = True
        web.ctx.orm.add(u)
        web.ctx.orm.commit()
        logout()
        return jsonify(success=True)
