#!/usr/lib/env python
# -*- coding: utf-8 -*-

import os.path

import celery.exceptions

from app.lib.pubsub import Publisher


class AvatarValidator(Publisher):
    """Validates an uploaded avatar.

    Verify that the client has successufully uploaded an avatar and that such
    file _ends_ with one of the supported extensions.  Note that for the latter
    check, only the extension of the filename is checked and not the content of
    the in-memory file (cgi standard).

    >>> from collections import namedtuple
    >>> class Subscriber(object):
    ...   def invalid_avatar(self, reason):
    ...     print 'Invalid: %(reason)s' % dict(reason=reason)
    ...   def valid_avatar(self, *args):
    ...     print 'Valid!'
    >>> File = namedtuple('File', 'filename file'.split())
    >>> this = AvatarValidator()
    >>> this.add_subscriber(Subscriber())

    >>> this.perform('')
    Invalid: Missing
    >>> this.perform({})
    Invalid: Missing

    >>> this.perform(File('foo.mp3', None))
    Invalid: Invalid format
    >>> this.perform(File('foo.doc', None))
    Invalid: Invalid format

    >>> this.perform(File('foo.jpg', None))
    Valid!
    >>> this.perform(File('foo.png', None))
    Valid!
    """

    """The set of valid avatar extensions."""
    valid_extensions = {'png', 'jpg', 'jpeg'}

    def perform(self, avatar):
        """Validates ``avatar`` and publish result messages accordingly.

        If avatar is empty (e.g. empty string or empty avatar) or its extension
        is not supported by the system, a 'invalid_form' message is published
        followed by the reason of the invalidation.

        Otherwise, a 'valid_avatar' message is published, with name of the name
        and the content of the in-memory file object.
        """
        if avatar == '' or avatar == {}:
            self.publish('invalid_avatar', 'Missing')
        else:
            _, ext = os.path.splitext(avatar.filename)
            ext = ext.lower().strip('.') 
            if ext not in self.valid_extensions:
                self.publish('invalid_avatar', 'Invalid format')
            else:
                self.publish('valid_avatar', avatar.file, avatar.filename)


class AvatarChangeTaskExecutor(Publisher):
    """Proxies the asynchronous execution of the homonym celery task.

    >>> from mock import Mock, MagicMock
    >>> class Subscriber(object):
    ...   def task_created(self, taskid):
    ...     print 'Spawned task %(id)s' % dict(id=taskid)
    >>> this = AvatarChangeTaskExecutor()
    >>> this.add_subscriber(Subscriber())

    >>> task = Mock(delay=MagicMock(return_value=42))
    >>> this.perform(task, 'userid', '/tmp/avatar2395iu/foo.png', None, None)
    Spawned task 42
    """

    def perform(self, task, userid, uploaded, destdir, baseurl):
        """Spawns ``task`` asynchronously and return the URL to use to check the
        status of the task.

        Arguments:
            task the task
            userid the ID of the caller
            uploaded the path of the uploaded file
            destdir the avatar destination directory
            baseurl the avatar base url
        """
        taskid = task.delay(userid, uploaded, destdir, baseurl)
        self.publish('task_created', taskid)


class AvatarChangeTaskStatusChecker(Publisher):
    """Proxies the operation of checking the status of a previously spawned
    asynchronous task.

    >>> from mock import Mock, MagicMock
    >>> class Subscriber(object):
    ...   def task_running(self, taskid):
    ...     print 'Still running: %(id)s' % dict(id=taskid)
    ...   def task_error(self, taskid, e):
    ...     print 'Oh noes! %(error)s' % dict(error=e)
    ...   def task_finished(self, taskid, r):
    ...     print 'Done: %(ret)s' % dict(ret=r)
    >>> this = AvatarChangeTaskStatusChecker()
    >>> this.add_subscriber(Subscriber())

    >>> exception = celery.exceptions.TimeoutError()
    >>> result = Mock(get=MagicMock(side_effect=exception))
    >>> task = Mock(AsyncResult=MagicMock(return_value=result))
    >>> this.perform(task, 42)
    Still running: 42

    >>> exception = ValueError('Shit happens!')
    >>> result = Mock(get=MagicMock(side_effect=exception))
    >>> task = Mock(AsyncResult=MagicMock(return_value=result))
    >>> this.perform(task, 42)
    Oh noes! Shit happens!

    >>> ret = 'Hell yeah!'
    >>> result = Mock(get=MagicMock(return_value=ret))
    >>> task = Mock(AsyncResult=MagicMock(return_value=result))
    >>> this.perform(task, 42)
    Done: Hell yeah!
    """

    def perform(self, task, taskid, timeout=0.1):
        """Checks the status of ``task`` and publish different messages in case
        an error occurred, the task is still running or it completed his job.

        If the task is still running, a 'task_running' message is published to
        subscribers, together with the id of the task;  if the task has finished,
        'task_finished' message is published, paired with the id of the task and
        its output;  finally, if something went wrong during the execution of
        the task, a 'task_error' will be published
        """
        future = task.AsyncResult(taskid)
        try:
            ret = future.get(timeout=timeout)
        except celery.exceptions.TimeoutError:
            self.publish('task_running', taskid)
        except Exception as e:
            self.publish('task_error', taskid, e)
        else:
            self.publish('task_finished', taskid, ret)
