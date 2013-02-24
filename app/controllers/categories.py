#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.sql import distinct
from sqlalchemy.sql import func

import web

from app.models import Expense
from app.models import Recurrence
from app.utils import protected
from app.utils import jsonify
from app.utils import BaseHandler



class CategoriesNamesHandler(BaseHandler):

    @protected
    def GET(self):
        categories1 = (
            web.ctx.orm.query(
                distinct(Expense.category), func.min(Expense.created))
                .filter_by(user_id=self.current_user().id)
                .group_by(Expense.category)
                .order_by(Expense.created)
                .all())
        categories2 = (
            web.ctx.orm.query(
                distinct(Recurrence.category), func.min(Recurrence.created))
                .filter_by(user_id=self.current_user().id)
                .group_by(Recurrence.category)
                .order_by(Recurrence.created)
                .all())
        categories = sorted(categories1 + categories2,
                            key=lambda c: c[1])
        return jsonify(
                categories=sorted([c[0] for c in categories]))
