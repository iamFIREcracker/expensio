#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Queue

import app.lib.avatar as avatar
import app.lib.fs as fs
import app.lib.logging as logging


TASK_RUNNING, TASK_FAILED, TASK_FINISHED = xrange(3)


def users_avatar_change(logger, file, fsadapter, task, avatardir, webavatardir,
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
