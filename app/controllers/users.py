#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

import web
from web.webapi import _status_code

import app.config
import app.tasks as tasks
import app.lib.avatar as avatar
import app.lib.forms as forms
import app.lib.fs as fs
import app.lib.logging as logging
import app.lib.users as users
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
        userid = self.current_user().id
        logger = logging.LoggingSubscriber(web.ctx.logger)
        validator = avatar.AvatarValidator()
        tempfilecreator = fs.TempFileCreator()
        fsadapter = fs.FileSystemAdapter()
        executor = avatar.AvatarChangeTaskExecutor()

        class AvatarValidatorSubscriber(object):
            def invalid_avatar(self, reason):
                content = jsonify(success=False, errors=dict(avatar=reason))
                raise ResponseContent(content)

            def valid_avatar(self, file, name):
                tempfilecreator.perform(fsadapter, file, name)

        class TempFileCreatorSubscriber(object):
            def tempfile_created(self, tempfile):
                executor.perform(tasks.UsersAvatarChangeTask, userid, tempfile,
                                 app.config.AVATAR_DIR,
                                 os.path.join(web.ctx.home,
                                              app.config.AVATAR_DIR))

        class TaskExecutorSubscriber(object):
            def task_created(self, location):
                web.header('Location', location)
                raise web.accepted()

        validator.add_subscriber(logger, AvatarValidatorSubscriber())
        tempfilecreator.add_subscriber(logger, TempFileCreatorSubscriber())
        executor.add_subscriber(logger, TaskExecutorSubscriber())
        try:
            # The dictionary used as default is needed by the framework to
            # convert the uploaded file, if any, to a FieldStorage object.
            #
            # If 'avatar' is present and it is actually a file then a
            # FieldStorage is created;  if 'avatar' is present but it is empty
            # (i.e. form submitted without specifying a file) then an emtpy
            # string is returned.  Finally (i.e. the field has not been set) an
            # emtpy dictionary is returned.
            validator.perform(web.input(avatar={}).avatar)
        except ResponseContent as r:
            return r.content


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
        logger = logging.LoggingSubscriber(web.ctx.logger)
        checker = avatar.AvatarChangeTaskStatusChecker()

        class StatusCheckerSubscriber(object):
            def task_running(self):
                raise web.ok()

            def task_error(self, exception):
                if type(exception).__name__ == 'IOError':
                    raise web.unsupportedmediatype()
                else:
                    web.ctx.logger.exception('Avatar change task aborted')
                    raise exception

            def task_complete(self, location):
                web.header('Location', location)
                raise web.created()

        checker.add_subscriber(logger, StatusCheckerSubscriber())
        checker.perform(tasks.UsersAvatarChangeTask, taskid)


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
        userid = self.current_user().id
        logger = logging.LoggingSubscriber(web.ctx.logger)
        avatarupdater = users.AvatarUpdater()

        class AvatarUpdaterSubscriber(object):
            def not_existing_user(self, user_id):
                message = 'Invalid user ID: %(id)s' % dict(id=user_id)
                raise ValueError(message)
            def avatar_updated(self, user_id, avatar):
                raise _status_code('204 No Content')

        avatarupdater.add_subscriber(logger, AvatarUpdaterSubscriber())
        avatarupdater.perform(Users, userid, None)


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
        userid = self.current_user().id
        logger = logging.LoggingSubscriber(web.ctx.logger)
        formvalidator = forms.FormValidator()
        userupdater = users.UserUpdater()

        class FormValidatorSubscriber(object):
            def invalid_form(self, errors):
                content = jsonify(success=False, errors=errors)
                raise ResponseContent(content)
            def valid_form(self, form):
                userupdater.perform(Users, userid, form.d.name, form.d.currency)

        class UserUpdaterSubscriber(object):
            def not_existing_user(self, user_id):
                message = 'Invalid user ID: %(id)s' % dict(id=user_id)
                raise ValueError(message)
            def user_updated(self, user_id, name, currency):
                raise _status_code('204 No Content')

        formvalidator.add_subscriber(logger, FormValidatorSubscriber())
        userupdater.add_subscriber(logger, UserUpdaterSubscriber())
        try:
            formvalidator.perform(users_edit(), describe_invalid_form)
        except ResponseContent as r:
            return r.content


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
        logger = logging.LoggingSubscriber(web.ctx.logger)
        userdeleter = users.UserDeleter()

        class UserDeleterSubscriber(object):
            def not_existing_user(self, user_id):
                message = 'Invalid user ID: %(id)s' % dict(id=user_id)
                raise ValueError(message)
            def user_deleted(self, user_id):
                logout()
                raise _status_code('204 No Content')

        userdeleter.add_subscriber(logger, UserDeleterSubscriber())
        userdeleter.perform(Users, self.current_user().id)
