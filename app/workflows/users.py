#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Queue

from app.forms import users_edit
import app.lib.avatar as avatar
import app.lib.forms as forms
import app.lib.fs as fs
import app.lib.logging as logging
import app.lib.users as users
from app.utils import describe_invalid_form


TASK_RUNNING, TASK_FAILED, TASK_FINISHED = xrange(3)


def change_avatar(logger, file, fsadapter, task, avatardir, webavatardir,
                  userid):
    logger = logging.LoggingSubscriber(logger)
    validator = avatar.AvatarValidator()
    tmpfilecreator = fs.TempFileCreator()
    executor = avatar.AvatarChangeTaskExecutor()
    queue = Queue.Queue()

    class AvatarValidatorSubscriber(object):
        def invalid_avatar(self, reason):
            queue.put((False, dict(success=False, errors=dict(avatar=reason))))

        def valid_avatar(self, file, name):
            tmpfilecreator.perform(fsadapter, file, name)

    class TempFileCreatorSubscriber(object):
        def tempfile_created(self, tempfile):
            executor.perform(task, userid, tempfile, avatardir, webavatardir)

    class TaskExecutorSubscriber(object):
        def task_created(self, location):
            queue.put((True, location))

    validator.add_subscriber(logger, AvatarValidatorSubscriber())
    tmpfilecreator.add_subscriber(logger, TempFileCreatorSubscriber())
    executor.add_subscriber(logger, TaskExecutorSubscriber())
    validator.perform(file)
    return queue.get()


def check_avatar_change_status(logger, task, taskid):
    logger = logging.LoggingSubscriber(logger)
    checker = avatar.AvatarChangeTaskStatusChecker()
    queue = Queue.Queue()

    class StatusCheckerSubscriber(object):
        def task_running(self, taskid):
            queue.put((TASK_RUNNING, None))

        def task_error(self, taskid, exception):
            queue.put((TASK_FAILED, exception))

        def task_finished(self, taskid, ret):
            queue.put((TASK_FINISHED, ret))

    checker.add_subscriber(logger, StatusCheckerSubscriber())
    checker.perform(task, taskid)
    return queue.get()


def remove_avatar(logger, repository, userid):
    logger = logging.LoggingSubscriber(logger)
    avatarupdater = users.AvatarUpdater()
    queue = Queue.Queue()

    class AvatarUpdaterSubscriber(object):
        def avatar_updated(self, user_id, avatar):
            queue.put((True, None))
        def not_existing_user(self, user_id):
            queue.put((False, dict(success=False, errors=dict(id='Invalid'))))

    avatarupdater.add_subscriber(logger, AvatarUpdaterSubscriber())
    avatarupdater.perform(repository, userid, None)
    return queue.get()


def edit_user(logger, params, repository, userid):
    logger = logging.LoggingSubscriber(logger)
    formvalidator = forms.FormValidator()
    userupdater = users.UserUpdater()
    queue = Queue.Queue()

    class FormValidatorSubscriber(object):
        def invalid_form(self, errors):
            queue.put((False, dict(success=False, errors=errors)))
        def valid_form(self, form):
            userupdater.perform(repository, userid, form.d.name,
                                form.d.currency)

    class UserUpdaterSubscriber(object):
        def user_updated(self, user_id, name, currency):
            queue.put((True, None))
        def not_existing_user(self, user_id):
            queue.put((False, dict(success=False, errors=dict(id='Invalid'))))

    formvalidator.add_subscriber(logger, FormValidatorSubscriber())
    userupdater.add_subscriber(logger, UserUpdaterSubscriber())
    formvalidator.perform(users_edit(), params, describe_invalid_form)
    return queue.get()


def delete_user(logger, repository, userid):
    logger = logging.LoggingSubscriber(logger)
    userdeleter = users.UserDeleter()
    queue = Queue.Queue()

    class UserDeleterSubscriber(object):
        def user_deleted(self, user_id):
            queue.put((True, None))
        def not_existing_user(self, user_id):
            queue.put((False, dict(success=False, errors=dict(id='Invalid'))))

    userdeleter.add_subscriber(logger, UserDeleterSubscriber())
    userdeleter.perform(repository, userid)
    return queue.get()
