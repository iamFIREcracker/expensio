#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import webtest

from tests.utils import change_avatar
from tests.utils import edit_profile
from tests.utils import delete_profile
from tests.utils import register
from tests.utils import remove_avatar
from tests.utils import wait_avatar_change
from tests.utils import url
from tests.utils import TestCaseWithApp



class TestProfile(TestCaseWithApp):

    def test_anonymous_user_cannot_access_the_profile_page(self):
        resp = self.app.get('/profile')
        self.assertEquals('302 Found', resp.status)
        self.assertEquals(url('/'), resp.location)

    def test_logged_user_can_view_the_profile_page(self):
        register(self.app)
        resp = self.app.get('/profile')
        self.assertEquals('200 OK', resp.status)
        self.assertIn('Avatar', resp)
        self.assertIn('Name', resp)
        self.assertIn('Currency', resp)
        self.assertIn('Google', resp)
        self.assertIn('Facebook', resp)
        self.assertIn('Twitter', resp)
        self.assertIn('Fake', resp)

    def test_http_accept_header_is_required_to_post_avatar_change(self):
        with self.assertRaises(webtest.AppError) as cm:
            self.app.post('/v1/users/invalid-uuid/avatar/change')
            self.assertEqual("Bad response: 406 Not Acceptable", cm.exception)

    def test_logged_user_cannot_post_avatar_change_of_another_user(self):
        register(self.app)
        with self.assertRaises(webtest.AppError) as cm:
            change_avatar('invalid-uuid', self.app)
            self.assertEqual("Bad response: 401 Unauthorized", cm.exception)

    def test_logged_user_cannot_post_avatar_change_without_specifying_it(self):
        user_id = register(self.app)
        resp = change_avatar(user_id, self.app)
        self.assertFalse(resp.json['success'],
                         'An error should have been received')
        self.assertIn('errors', resp.json)
        self.assertIn('avatar', resp.json['errors'])

    def test_logged_user_cannot_post_avatar_change_specifying_non_image(self):
        user_id = register(self.app)
        resp = change_avatar(user_id, self.app, __file__)
        self.assertFalse(resp.json['success'],
                         'An error should have been received')
        self.assertIn('errors', resp.json)
        self.assertIn('avatar', resp.json['errors'])

    def test_logged_user_can_post_avatar_change(self):
        user_id = register(self.app)
        resp = change_avatar(user_id, self.app, 'tests/avatar.png')
        self.assertEquals('202 Accepted', resp.status)
        self.assertIn('avatar/change/status', resp.location)

    def test_http_accept_header_is_required_to_check_avatar_change_status(self):
        with self.assertRaises(webtest.AppError) as cm:
            self.app.get('/v1/users/invalid-uuid/avatar/change/status/invalid-uuid')
            self.assertEqual("Bad response: 406 Not Acceptable", cm.exception)

    def test_logged_user_cannot_check_avatar_change_status_of_another_user(self):
        register(self.app)
        with self.assertRaises(webtest.AppError) as cm:
            self.app.get(
                    '/v1/users/invalid-uuid/avatar/change/status/invalid-uuid',
                    extra_environ=dict(
                        HTTP_ACCEPT='application/json'
                    ))
            self.assertEqual("Bad response: 401 Unauthorized", cm.exception)

    def test_logged_user_can_change_avatar(self):
        user_id = register(self.app)
        resp = change_avatar(user_id, self.app, 'tests/avatar.png')

        resp = wait_avatar_change(resp.location, self.app, 10)
        self.assertEquals('201 Created', resp.status)
        self.assertIn('.png', resp.location)

    def test_http_accept_header_is_required_to_remove_avatar(self):
        with self.assertRaises(webtest.AppError) as cm:
            self.app.post('/v1/users/invalid-uuid/avatar/remove')
            self.assertEqual("Bad response: 406 Not Acceptable", cm.exception)

    def test_logged_user_cannot_remove_avatar_of_another_user(self):
        register(self.app)
        with self.assertRaises(webtest.AppError) as cm:
            remove_avatar('invalid-uuid', self.app)
            self.assertEqual("Bad response: 401 Unauthorized", cm.exception)

    def test_logged_user_can_remove_avatar(self):
        user_id = register(self.app)
        resp = remove_avatar(user_id, self.app)
        self.assertEquals('204 No Content', resp.status)

    def test_http_accept_header_is_required_to_update_profile(self):
        with self.assertRaises(webtest.AppError) as cm:
            self.app.post('/v1/users/invalid-uuid/edit')
            self.assertEqual("Bad response: 406 Not Acceptable", cm.exception)

    def test_logged_user_cannot_update_profile_of_another_user(self):
        register(self.app)
        with self.assertRaises(webtest.AppError) as cm:
            edit_profile('invalid-uuid', self.app)
            self.assertEqual("Bad response: 401 Unauthorized", cm.exception)

    def test_logged_user_cannot_update_profile_with_invalid_currency(self):
        user_id = register(self.app)
        resp = edit_profile(user_id, self.app, name='name', currency='invalid')
        self.assertFalse(
                resp.json['success'], 'An error should have been received')
        self.assertIn('errors', resp.json)
        self.assertIn('currency', resp.json['errors'])

    def test_logged_user_can_update_profile(self):
        user_id = register(self.app)
        resp = edit_profile(user_id, self.app, name='name', currency='$')
        self.assertEquals('204 No Content', resp.status)

    def test_http_accept_header_is_required_to_delete_user(self):
        with self.assertRaises(webtest.AppError) as cm:
            self.app.post('/v1/users/invalid-uuid/delete')
            self.assertEqual("Bad response: 406 Not Acceptable", cm.exception)

    def test_logged_user_cannot_delete_profile_of_another_user(self):
        register(self.app)
        with self.assertRaises(webtest.AppError) as cm:
            delete_profile('invalid-uuid', self.app)
            self.assertEqual("Bad response: 401 Unauthorized", cm.exception)

    def test_logged_user_can_delete_profile(self):
        user_id = register(self.app)
        resp = delete_profile(user_id, self.app)
        self.assertEquals('204 No Content', resp.status)
