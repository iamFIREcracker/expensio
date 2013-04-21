#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.utils import login
from tests.utils import TestCaseWithApp


class TestProfile(TestCaseWithApp):

    def test_anonymous_user_cannot_access_the_profile_page(self):
        resp = self.app.get('/profile')
        self.assertEquals('302 Found', resp.status)

    def test_logged_user_can_view_the_profile_page(self):
        login(self.app)
        resp = self.app.get('/profile')
        self.assertEquals('200 OK', resp.status)
        self.assertIn('Avatar', resp)
        self.assertIn('Name', resp)
        self.assertIn('Currency', resp)
        self.assertIn('Google', resp)
        self.assertIn('Facebook', resp)
        self.assertIn('Twitter', resp)
        self.assertIn('Fake', resp)
