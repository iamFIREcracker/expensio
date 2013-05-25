#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

import web
from web.webapi import _status_code

import app.config
import app.tasks as tasks
import app.lib.forms as forms
import app.lib.fs as fs
import app.lib.logging as logging
import app.lib.users as users
import app.workflows.users as workflows
from app.exceptions import ResponseContent
from app.forms import users_edit
from app.managers import Users
from app.tools.request_decorators import api
from app.utils import describe_invalid_form
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

        On error an object of the specified media format containing error
        descriptions will be sent back to the caller:
        {
            "success": false,
            "errors":
            {
                "avatar": "Required"
            }
        }
        """
        # The dictionary used as default is needed by the framework to convert
        # the uploaded file, if any, to a FieldStorage object.  If 'avatar' is
        # present and it is actually a file then a FieldStorage is created;  if
        # 'avatar' is present but it is empty (i.e. form submitted without
        # specifying a file) then an emtpy string is returned.  Finally (i.e.
        # the field has not been set) an emtpy dictionary is returned.
        file = web.input(avatar={}).avatar
        webavatardir = os.path.join(web.ctx.home, app.config.AVATAR_DIR)
        ok, arg = workflows.change_avatar(web.ctx.logger, file,
                                          fs.FileSystemAdapter(),
                                          tasks.UsersAvatarChangeTask,
                                          app.config.AVATAR_DIR,
                                          webavatardir, id)
        if not ok:
            return jsonify(**arg)
        else:
            location = '/v1/users/%(userid)s/avatar/change/status/%(taskid)s'
            location = location % dict(userid=id, taskid=arg)
            web.header('Location', location)
            raise web.accepted()


class UsersAvatarChangeStatusHandler(BaseHandler):

    @api
    @protected
    @me
    def GET(self, id, taskid):
        """Checks the status of a pending 'avatar-change' operation.

        The 'HTTP_ACCEPT' header is required to allow the controller to specify
        the acceptable media type for the response.

        There should be a logged-in user behind this request.

        The specified ``id`` should match the one of the logged-in user.

        If all these prerequisites hold true then the controller will check the 
        status of a task with ID ``taskid``.

        If the task is still active the controller will return '200 OK'; 
        clients are then supposed to come later and check again the status of the
        task.

        On the other hand a '201 Created' status message with the 'Location'
        header pointing to the uploaded avatar will be sent back to client if
        the task has exited normally.

        Note that a '415 Unsupported Media Type' status message is returned if
        the format of the uploaded avatar cannot be handled by the server.
        """
        task = tasks.UsersAvatarChangeTask
        status, arg = workflows.check_avatar_change_status(web.ctx.logger,
                                                           task, taskid)
        if status == workflows.TASK_RUNNING:
            raise web.ok()
        elif status == workflows.TASK_FAILED:
            if type(arg).__name__ == 'IOError':
                raise web.unsupportedmediatype()
            else:
                raise arg
        else:
            assert status == workflows.TASK_FINISHED
            web.header('Location', arg)
            raise web.created()


class UsersAvatarRemove(BaseHandler):

    @api
    @protected
    @me
    def POST(self, id):
        """Removes the avatar of the user identified by ``id``.

        The 'HTTP_ACCEPT' header is required to allow the controller to specify
        the acceptable media type for the response.

        There should be a logged-in user behind this request.

        The specified ``id`` should match the one of the logged-in user.

        If all these prerequisites hold true then the controller will unlink the
        avatar, if any, from the logged-in user.

        On success the controller will clear the 'avatar' property of the
        logged-in user and then return '204 No Content' back to the client.
        """
        ok, arg = workflows.remove_avatar(web.ctx.logger, Users, id)
        if not ok:
            return jsonify(**arg)
        else:
            raise _status_code('204 No Content')


class UsersEditHandler(BaseHandler):
    
    @api
    @protected
    @me
    def POST(self, id):
        """Changes one or more properties of the user identified by ``id``.

        The 'HTTP_ACCEPT' header is required to allow the controller to specify
        the acceptable media type for the response.

        There should be a logged-in user behind this request.

        The specified ``id`` should match the one of the logged-in user.

        If all these prerequisites hold true then the controller will try to
        update the logged-in user.

        On success the controller will return '204 No Content'.

        On error (e.g. one or more submitted fields are invalid), an object of
        the specified media format containing error descriptions will be sent
        back to the caller:
        {
            "success": false,
            "errors":
            {
                "currency": "Unknown"
            }
        }
        """
        ok, arg = workflows.edit_user(web.ctx.logger, web.input(), Users, id)
        if not ok:
            return jsonify(**arg)
        else:
            raise _status_code('204 No Content')


class UsersDeleteHandler(BaseHandler):

    @api
    @protected
    @me
    def POST(self, id):
        """Deletes the user identified by ``id``.

        The 'HTTP_ACCEPT' header is required to allow the controller to specify
        the acceptable media type for the response.

        There should be a logged-in user behind this request.

        The specified ``id`` should match the one of the logged-in user.

        If all these prerequisites hold true then the controller will delete
        (deactivate) the logged-in user.

        On success the controller will return '204 No Content'.
        """
        ok, arg = workflows.delete_user(web.ctx.logger, Users, id)
        if not ok:
            return jsonify(**arg)
        else:
            logout()
            raise _status_code('204 No Content')
