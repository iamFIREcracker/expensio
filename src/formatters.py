#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from config import DATE_FORMAT



def dateformatter(value, format_=DATE_FORMAT):
    """
    Convert the input `datetime` object into a string
    """
    return datetime.strftime(value, format_)
