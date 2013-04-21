#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.utils import url
from tests.utils import login
from tests.utils import TestCaseWithApp


class TestApplication(TestCaseWithApp):

    def test_anonymous_user_is_presented_with_the_info_page(self):
        resp = self.app.get('/')
        self.assertEquals('200 OK', resp.status)
        self.assertTrue(
                'Try it!' in resp, 'Fake register link missing')

    def test_logged_user_is_presented_the_main_page(self):
        login(self.app)
        resp = self.app.get('/')
        self.assertEquals('200 OK', resp.status)
        self.assertTrue(
                'Fake Name' in resp, 'Name of the user missing')
        self.assertTrue(
                'By Date' in resp, 'By-Date widget missing')
        self.assertTrue(
                'Income' in resp, 'Income widget missing')
        self.assertTrue(
                'Outcome' in resp, 'Outcome widget missing')
