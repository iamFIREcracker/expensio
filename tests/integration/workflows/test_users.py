#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from mock import Mock
from mock import MagicMock

from app.workflows.users import users_avatar_change


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
