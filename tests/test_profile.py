#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webtest

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

    def test_http_accept_header_is_required_to_change_avatar(self):
        with self.assertRaises(webtest.AppError) as cm:
            self.app.post('/v1/users/invalid-uuid/avatar/change')
            self.assertEqual(
                    "Bad response: 406 Not Acceptable", cm.exception)

    def test_logged_user_cannot_change_avatar_of_another_user(self):
        register(self.app)
        with self.assertRaises(webtest.AppError) as cm:
            self.app.post(
                    '/v1/users/invalid-uuid/avatar/change', extra_environ=dict(
                        HTTP_ACCEPT='application/json'
                    ))
            self.assertEqual(
                    "Bad response: 401 Unauthorized", cm.exception)

    def test_logged_user_cannot_change_avatar_without_specifying_it(self):
        user_id = register(self.app)
        resp = self.app.post(
                '/v1/users/%(user_id)s/avatar/change' % dict(user_id=user_id),
                extra_environ=dict(HTTP_ACCEPT='application/json'))
        self.assertFalse(
                resp.json['success'], 'An error should have been received')

    def test_logged_user_can_change_avatar(self):
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

        resp = self.app.get(resp.location, extra_environ=dict(
            HTTP_ACCEPT='application/json'
        ))

        self.assertEquals('201 Created', resp.status)
        self.assertTrue(
                resp.location.startswith(url('/static/avatars/')),
                'The redirect should point to a static resource')
