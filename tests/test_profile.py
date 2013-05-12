#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import webtest

from tests.utils import edit_profile
from tests.utils import post_avatar_change
from tests.utils import register
from tests.utils import upload
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
            self.assertEqual(
                    "Bad response: 406 Not Acceptable", cm.exception)

    def test_logged_user_cannot_post_avatar_change_of_another_user(self):
        register(self.app)
        with self.assertRaises(webtest.AppError) as cm:
            self.app.post(
                    '/v1/users/invalid-uuid/avatar/change', extra_environ=dict(
                        HTTP_ACCEPT='application/json'
                    ))
            self.assertEqual(
                    "Bad response: 401 Unauthorized", cm.exception)

    def test_logged_user_cannot_post_avatar_change_without_specifying_it(self):
        user_id = register(self.app)
        resp = self.app.post(
                '/v1/users/%(user_id)s/avatar/change' % dict(user_id=user_id),
                extra_environ=dict(HTTP_ACCEPT='application/json'))
        self.assertFalse(
                resp.json['success'], 'An error should have been received')
        self.assertIn('errors', resp.json)
        self.assertIn('avatar', resp.json['errors'])

    def test_logged_user_can_post_avatar_change(self):
        user_id = register(self.app)
        resp = self.app.post(
                '/v1/users/%(user_id)s/avatar/change' % dict(user_id=user_id),
                dict(avatar=upload('tests/avatar.png')), extra_environ=dict(
                    HTTP_ACCEPT='application/json'
                ))
        self.assertEquals('202 Accepted', resp.status)
        self.assertTrue(
            resp.location.startswith(
                    '/v1/users/%(user_id)s/avatar/change/' % dict(
                        user_id=user_id
                    )))

    def test_http_accept_header_is_required_to_check_avatar_change_status(self):
        with self.assertRaises(webtest.AppError) as cm:
            self.app.get('/v1/users/invalid-uuid/avatar/change/status/invalid-uuid')
            self.assertEqual(
                    "Bad response: 406 Not Acceptable", cm.exception)

    def test_logged_user_cannot_check_avatar_change_status_of_another_user(self):
        register(self.app)
        with self.assertRaises(webtest.AppError) as cm:
            self.app.get(
                    '/v1/users/invalid-uuid/avatar/change/status/invalid-uuid',
                    extra_environ=dict(
                        HTTP_ACCEPT='application/json'
                    ))
            self.assertEqual(
                    "Bad response: 401 Unauthorized", cm.exception)

    def test_logged_user_cannot_change_avatar_with_a_not_image_file(self):
        user_id = register(self.app)
        resp = post_avatar_change(user_id, __file__, self.app)

        # Wait for the async task to complete
        time.sleep(1.0)

        with self.assertRaises(webtest.AppError) as cm:
            self.app.get(resp.location, extra_environ=dict(
                HTTP_ACCEPT='application/json'
            ))
            self.assertEqual(
                    "Bad response: 415 Unsupported Media Type", cm.exception)

    def test_logged_user_can_change_avatar(self):
        user_id = register(self.app)
        resp = post_avatar_change(user_id, 'tests/avatar.png', self.app)

        # Wait for the async task to complete
        time.sleep(1.0)

        resp = self.app.get(resp.location, extra_environ=dict(
            HTTP_ACCEPT='application/json'
        ))

        self.assertEquals('201 Created', resp.status)
        self.assertTrue(
                resp.location.startswith(url('/static/avatars/')),
                'The redirect should point to a static resource')

    def test_http_accept_header_is_required_to_remove_avatar(self):
        with self.assertRaises(webtest.AppError) as cm:
            self.app.post('/v1/users/invalid-uuid/avatar/remove')
            self.assertEqual("Bad response: 406 Not Acceptable", cm.exception)

    def test_logged_user_cannot_remove_avatar_of_another_user(self):
        register(self.app)
        with self.assertRaises(webtest.AppError) as cm:
            self.app.post('/v1/users/invalid-uuid/avatar/remove',
                          extra_environ=dict(HTTP_ACCEPT='application/json'))
            self.assertEqual("Bad response: 401 Unauthorized",
                             cm.exception)

    def test_logged_user_can_remove_avatar(self):
        user_id = register(self.app)
        url = '/v1/users/%(user_id)s/avatar/remove' % dict(user_id=user_id)
        resp = self.app.post(url,
                             extra_environ=dict(HTTP_ACCEPT='application/json'))
        self.assertEquals('200 OK', resp.status)

    def test_http_accept_header_is_required_to_update_profile(self):
        with self.assertRaises(webtest.AppError) as cm:
            edit_profile('invalid-uuid', self.app)
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
