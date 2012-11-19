#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from config import DATE_FORMAT



def dateformatter(value):
    return datetime.strftime(value, DATE_FORMAT)
