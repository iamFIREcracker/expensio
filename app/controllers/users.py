#!/usr/bin/env python
# -*- coding: utf-8 -*-

import celery
import web

import app.tasks as tasks
from app.forms import users_avatar
from app.forms import users_edit
from app.serializers import UserSerializer
from app.upload import UploadedFile
from app.tools.request_decorators import api
from app.utils import accepted
from app.utils import jsonify
from app.utils import logout
from app.utils import me
from app.utils import protected
from app.utils import BaseHandler



class UsersAvatarChange(BaseHandler):

    @api
    @protected
    @me
    def POST(self, id):
        """Changes the avatar of the user identified by ``id``.

        The 'HTTP_ACCEPT' header is required to allow the controller to specify
        the acceptable media type for the response.

        There should be a logged-in user behind this request.

        The specified ``id`` should match the one of the logged-in user.

        If all these prerequisites hold true then the controller will check for 
        the existence of the field ``avatar`` containing an uploaded file.

        On success the controller will spawn an asynchronous task (in charge of
        processing the image) and will return '202 Accepted'.  Note that the
        'Location' header will be filled with the URI handy to check the status
        of the asynchronous task.

        On error an object with error descriptions and of the specified media
        format is returned to the caller:
        {
            "success": false,
            "errors":
            [
                "avatar": "Missing"
            ]
        }
        """
        avatar = UploadedFile('avatar')
        form = users_avatar()

        if not form.validates():
            return jsonify(success=False,
                    errors=dict((i.name, i.note) for i in form.inputs
                        if i.note is not None))
        else:
            task_id = tasks.UsersAvatarChangeTask.delay(
                    avatar, web.ctx.avatarman, self.current_user(),
                    web.ctx.home).task_id
            web.header(
                    'Location',
                    '/users/%(user_id)s/avatar/change/status/%(task_id)s' % dict(
                        user_id=self.current_user().id, task_id=task_id
                    ))
            raise web.accepted()


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
