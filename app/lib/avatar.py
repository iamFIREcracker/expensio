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

    >>> class Task(object):
    ...   def delay(self, *args, **kwargs):
    ...     print 'Spawned task'
    ...     return 42
    >>> class Subscriber(object):
    ...   def task_created(self, status):
    ...     print status
    >>> this = AvatarChangeTaskExecutor()
    >>> this.add_subscriber(Subscriber())

    >>> this.perform(Task(), 'myuserid', '/tmp/avatar2395iu/foo.png', None, None)
    Spawned task
    /v1/users/myuserid/avatar/change/status/42
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
        url = '/v1/users/%(userid)s/avatar/change/status/%(taskid)s'
        url = url % dict(userid=userid, taskid=taskid)
        self.publish('task_created', url)


class AvatarChangeTaskStatusChecker(Publisher):
    """Proxies the operation of checking the status of a previously spawned
    asynchronous task.

    >>> class Task(object):
    ...   def __init__(self, callable):
    ...     self.callable = callable
    ...   def AsyncResult(self, taskid):
    ...     return self
    ...   def get(self, *args, **kwargs):
    ...     return callable()
    >>> class Subscriber(object):
    ...   def task_running(self):
    ...     print 'Still running'
    ...   def task_error(self, e):
    ...     print 'Oh noes! %(exception)s' % dict(exception=e)
    ...   def task_complete(self, r):
    ...     print 'Done: %(ret)s' % dict(ret=r)
    >>> this = AvatarChangeTaskStatusChecker()
    >>> this.add_subscriber(Subscriber())

    >>> def callable():
    ...   raise celery.exceptions.TimeoutError()
    >>> this.perform(Task(callable), 42)
    Still running

    >>> def callable():
    ...   raise ValueError('Shit happens!')
    >>> this.perform(Task(callable), 42)
    Oh noes! Shit happens!

    >>> def callable():
    ...   return 'Hell yeah!'
    >>> this.perform(Task(callable), 42)
    Done: Hell yeah!
    """

    def perform(self, task, taskid, timeout=0.1):
        """Checks the status of ``task`` and publish different messages in case
        an error occurred, the task is still running or it completed his job."""
        future = task.AsyncResult(taskid)
        try:
            ret = future.get(timeout=timeout)
        except celery.exceptions.TimeoutError:
            self.publish('task_running')
        except Exception as e:
            self.publish('task_error', e)
        else:
            self.publish('task_complete', ret)
