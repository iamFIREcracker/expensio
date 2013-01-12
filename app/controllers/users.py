#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web

from app.forms import users_edit
from app.utils import me
from app.utils import protected
from app.utils import BaseHandler


class UsersEditHandler(BaseHandler):
    @protected
    @me
    def GET(self, id):
        form = users_edit()
        user = self.current_user()
        form.fill(id=user.id, name=user.name, currency=user.currency)
        return web.ctx.render.users_edit_complete(user=self.current_user(),
                users_edit=form)

    @protected
    @me
    def POST(self, id):
        form = users_edit()
        if form.validates():
            u = self.current_user()
            u.name = form.d.name
            u.currency = form.d.currency
            web.ctx.orm.add(u)
        return web.ctx.render.users_edit(users_edit=form)
