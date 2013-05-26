#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.utils import register
from tests.utils import TestCaseWithApp


class TestIndex(TestCaseWithApp):

    def test_anonymous_user_is_presented_with_the_info_page(self):
        resp = self.app.get('/')
        self.assertEquals('200 OK', resp.status)
        self.assertTrue(
                'Try it!' in resp, 'Fake register link missing')

    def test_logged_user_is_presented_the_main_page(self):
        register(self.app)
        resp = self.app.get('/')
        self.assertEquals('200 OK', resp.status)
        self.assertIn('Fake Name', resp)
        self.assertIn('By Date', resp)
        self.assertIn('Income', resp)
        self.assertIn('Outcome', resp)

    def test_logged_user_can_decide_which_period_to_display(self):
        register(self.app)
        resp = self.app.get('/2012/12')
        self.assertEquals('200 OK', resp.status)
        self.assertIn('2012, 12', resp)
