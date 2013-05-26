#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from web.form import Form
from web.form import Input

from app.utils import describe_invalid_form


class TestAppUtils(unittest.TestCase):

    def test_describe_invalid_form_with_valid_form(self):
        # Given
        input1 = Input('input1')
        input2 = Input('input2')
        input3 = Input('input3')
        form = Form(input1, input2, input3)

        # When
        desc = describe_invalid_form(form)

        # Then
        self.assertEquals(dict(), desc)

    def test_describe_invalid_form_with_at_least_one_invalid_input_field(self):
        # Given
        input1 = Input('input1')
        input1.note = 'Required'
        input2 = Input('input2')
        input3 = Input('input3')
        input3.note = 'Invalid: YYYY/MM/DD'
        form = Form(input1, input2, input3)

        # When
        desc = describe_invalid_form(form)

        # Then
        self.assertEquals(dict(input1='Required', input3='Invalid: YYYY/MM/DD'),
                          desc)
