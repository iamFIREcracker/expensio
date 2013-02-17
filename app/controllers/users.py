#!/usr/bin/env python
# -*- coding: utf-8 -*-

import celery
import web

import app.tasks as tasks
from app.forms import users_avatar
from app.forms import users_connect
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
        u = web.ctx.orm.merge(u)
        return jsonify(success=True, user=UserWrapper(u))


class UsersProfileHandler(BaseHandler):
    @protected
    def GET(self):
        user = self.current_user()
        avatar = users_avatar()
        avatar.fill(id=user.id, avatar=user.avatar)
        connect = users_connect()
        connect.fill(google=(user.google_id is not None),
                     facebook=(user.facebook_id is not None),
                     twitter=(user.twitter_id is not None),
                     fake=(not any([user.google_id is not None,
                                    user.facebook_id is not None,
                                    user.twitter_id is not None])))
        edit = users_edit()
        edit.fill(id=user.id, name=user.name, currency=user.currency)
        return web.ctx.render.profile(user=self.current_user(),
                users_avatar=avatar, users_connect=connect, users_edit=edit)


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
