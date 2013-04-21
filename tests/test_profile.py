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
        self.assertTrue(
                'Avatar' in resp, 'Avatar field missing')
        self.assertTrue(
                'Name' in resp, 'Name field missing')
        self.assertTrue(
                'Currency' in resp, 'Currency field missing')
        self.assertTrue(
                'Google' in resp, 'Google connect field missing')
        self.assertTrue(
                'Facebook' in resp, 'Facebook connect field missing')
        self.assertTrue(
                'Twitter' in resp, 'Twitter connect field missing')
        self.assertTrue(
                'Fake' in resp, 'Fake connect field missing')
