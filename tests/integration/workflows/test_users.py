#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import celery

from mock import Mock
from mock import MagicMock

from app.workflows.users import change_avatar
from app.workflows.users import check_avatar_change_status
from app.workflows.users import delete_user
from app.workflows.users import edit_user
from app.workflows.users import remove_avatar
from app.workflows.users import TASK_RUNNING, TASK_FAILED, TASK_FINISHED


class TestChangeAvatarWorkflow(unittest.TestCase):
    
    def test_without_avatar_should_return_error(self):
        # Given
        logger = Mock()
        file = ''

        # When
        ok, ret = change_avatar(logger, file, None, None, None, None, None)

        # Then
        self.assertFalse(ok)
        self.assertFalse(ret['success'])
        self.assertEquals('Missing', ret['errors']['avatar'])

    def test_with_invalid_avatar_should_return_error(self):
        # Given
        logger = Mock()
        file = Mock(filename='document.pdf')

        # When
        ok, ret = change_avatar(logger, file, None, None, None, None, None)

        # Then
        self.assertFalse(ok)
        self.assertFalse(ret['success'])
        self.assertEquals('Invalid format', ret['errors']['avatar'])

    def test_with_valid_avatar_and_oserror_should_raise_the_oserror(self):
        # Given
        logger = Mock()
        file = Mock(filename='avatar.png')
        fsadapter = Mock(tempfile=Mock(side_effect=OSError('Cannot write')))

        # When / Then
        with self.assertRaises(OSError) as cm:
            change_avatar(logger, file, fsadapter, None, None, None, None)
            self.assertEqual('Cannot write', cm.exception)

    def test_with_valid_avatar_should_return_the_taskid(self):
        # Given
        logger = Mock()
        file = Mock(filename='avatar.png')
        fsadapter = Mock(tempfile=MagicMock(return_value='/tmp/avatar.png'))
        task = Mock(delay=MagicMock(return_value='taskid'))

        # When 
        ok, taskid = change_avatar(logger, file, fsadapter, task,
                                   'avatars', 'http://localhost/avatars', None)

        # Then
        self.assertTrue(ok)
        self.assertEquals('taskid', taskid)


class TestCheckAvatarChangeStatusWorkflow(unittest.TestCase):
    
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


class TestRemoveAvatarWorkflow(unittest.TestCase):

    def test_cannot_remove_avatar_of_non_existing_user(self):
        # Given
        logger = Mock()
        repository = Mock(change_avatar=MagicMock(return_value=False))

        # When
        ok, ret = remove_avatar(logger, repository, None)

        # Then
        self.assertFalse(ok)
        self.assertFalse(ret['success'])
        self.assertEquals('Invalid', ret['errors']['id'])

    def test_remove_avatar_from_existing_user_should_return_success(self):
        # Given
        logger = Mock()
        repository = Mock(change_avatar=MagicMock(return_value=True))

        # When
        ok, _ = remove_avatar(logger, repository, None)

        # Then
        self.assertTrue(ok)


class TestEditUserWorkflow(unittest.TestCase):

    def test_cannot_edit_user_without_specifying_name(self):
        # Given
        logger = Mock()
        params = dict(currency='$')

        # When
        ok, ret = edit_user(logger, params, None, None)

        # Then
        self.assertFalse(ok)
        self.assertFalse(ret['success'])
        self.assertEquals('Required', ret['errors']['name'])

    def test_cannot_edit_user_without_specifying_currency(self):
        # Given
        logger = Mock()
        params = dict(name='John Smith')

        # When
        ok, ret = edit_user(logger, params, None, None)

        # Then
        self.assertFalse(ok)
        self.assertFalse(ret['success'])
        self.assertIn('currency', ret['errors'])

    def test_cannot_edit_user_specifying_an_invalid_currency(self):
        # Given
        logger = Mock()
        params = dict(name='John Smith', currency='asd')

        # When
        ok, ret = edit_user(logger, params, None, None)

        # Then
        self.assertFalse(ok)
        self.assertFalse(ret['success'])
        self.assertIn('currency', ret['errors'])

    def test_cannot_edit_non_existing_user(self):
        # Given
        logger = Mock()
        params = dict(name='John Smith', currency='$')
        repository = Mock(update=MagicMock(return_value=False))

        # When
        ok, ret = edit_user(logger, params, repository, None)

        # Then
        self.assertFalse(ok)
        self.assertFalse(ret['success'])
        self.assertEquals('Invalid', ret['errors']['id'])

    def test_can_edit_existing_user(self):
        # Given
        logger = Mock()
        params = dict(name='John Smith', currency='$')
        repository = Mock(update=MagicMock(return_value=True))

        # When
        ok, _ = edit_user(logger, params, repository, None)

        # Then
        self.assertTrue(ok)


class TestDeleteUserWorkflow(unittest.TestCase):

    def test_cannot_delete_non_existing_user(self):
        # Given
        logger = Mock()
        repository = Mock(delete=MagicMock(return_value=False))

        # When
        ok, ret = delete_user(logger, repository, None)

        # Then
        self.assertFalse(ok)
        self.assertFalse(ret['success'])
        self.assertEquals('Invalid', ret['errors']['id'])

    def test_remove_avatar_from_existing_user_should_return_success(self):
        # Given
        logger = Mock()
        repository = Mock(delete=MagicMock(return_value=True))

        # When
        ok, _ = delete_user(logger, repository, None)

        # Then
        self.assertTrue(ok)
