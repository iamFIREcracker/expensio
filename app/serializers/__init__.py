#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from .categories import CategorySerializer
from .expenses import ExpenseSerializer
from .stats import StatByCategorySerializer
from .stats import StatByDaySerializer


class JSONSerializer(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'to_dict'):
            return o.to_dict()
        else:
            return json.JSONEncoder.default(self, o)
            #return super(json.JSONEncoder, self).default(o)


__all__ = [CategorySerializer, ExpenseSerializer, StatByCategorySerializer,
           StatByDaySerializer]
