#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.sql import distinct

import web

from app.models import Expense
from app.utils import protected
from app.utils import jsonify
from app.utils import BaseHandler



class CategoriesNamesHandler(BaseHandler):

    @protected
    def GET(self):
        categories = (web.ctx.orm.query(distinct(Expense.category))
                .filter_by(user_id=self.current_user().id)
                .order_by(Expense.created))
        return jsonify(
                categories=sorted([c[0] for c in categories]))
