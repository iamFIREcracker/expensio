#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import celery

from mock import Mock
from mock import MagicMock

from app.workflows.users import users_avatar_change
from app.workflows.users import check_avatar_change_status
from app.workflows.users import TASK_RUNNING, TASK_FAILED, TASK_FINISHED


class TestUsersAvatarChange(unittest.TestCase):
    
    def test_without_avatar_should_return_error(self):
        # Given
        logger = Mock()
        file = ''

        # When
        _, ret = users_avatar_change(logger, file, None, None, None, None, None)

        # Then
        self.assertFalse(ret['success'])
        self.assertEquals('Missing', ret['errors']['avatar'])

    def test_with_invalid_avatar_should_return_error(self):
        # Given
        logger = Mock()
        file = Mock(filename='document.pdf')

        # When
        _, ret = users_avatar_change(logger, file, None, None, None, None, None)

        # Then
        self.assertFalse(ret['success'])
        self.assertEquals('Invalid format', ret['errors']['avatar'])

    def test_with_valid_avatar_and_oserror_should_raise_the_oserror(self):
        # Given
        logger = Mock()
        file = Mock(filename='avatar.png')
        fsadapter = Mock(tempfile=Mock(side_effect=OSError('Cannot write')))

        # When / Then
        with self.assertRaises(OSError) as cm:
            users_avatar_change(logger, file, fsadapter, None, None, None, None)
            self.assertEqual('Cannot write', cm.exception)

    def test_with_valid_avatar_should_return_the_taskid(self):
        # Given
        logger = Mock()
        file = Mock(filename='avatar.png')
        fsadapter = Mock(tempfile=MagicMock(return_value='/tmp/avatar.png'))
        task = Mock(delay=MagicMock(return_value='taskid'))

        # When 
        _, taskid = users_avatar_change(logger, file, fsadapter, task,
                                        'avatars', 'http://localhost/avatars',
                                        None)

        # Then
        self.assertEquals('taskid', taskid)


class TestCheckAvatarChangeStatus(unittest.TestCase):
    
    def test_check_status_of_running_task_should_return_running_status(self):
        # Given
        logger = Mock()
        exception = celery.exceptions.TimeoutError()
        result = Mock(get=MagicMock(side_effect=exception))
        task = Mock(AsyncResult=MagicMock(return_value=result))

        # When
        status, _ = check_avatar_change_status(logger, task, None)

        # Then
        self.assertEqual(TASK_RUNNING, status)

    def test_check_status_of_task_throwing_excetion_should_return_failed_status(self):
        # Given
        logger = Mock()
        exception = ValueError('Shit happens!')
        result = Mock(get=MagicMock(side_effect=exception))
        task = Mock(AsyncResult=MagicMock(return_value=result))

        # When
        status, exception = check_avatar_change_status(logger, task, None)

        # Then
        self.assertEqual(TASK_FAILED, status)
        self.assertEqual('Shit happens!', str(exception))

    def test_check_status_of_finished_task_should_return_finished_status(self):
        # Given
        logger = Mock()
        result = Mock(get=MagicMock(return_value='taskresult'))
        task = Mock(AsyncResult=MagicMock(return_value=result))

        # When
        status, result = check_avatar_change_status(logger, task, None)

        # Then
        self.assertEqual(TASK_FINISHED, status)
        self.assertEqual('taskresult', result)
