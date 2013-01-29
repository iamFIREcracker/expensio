#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web

from app.forms import users_edit
from app.forms import users_delete
from app.utils import jsonify
from app.utils import logout
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


class UsersDeleteHandler(BaseHandler):
    @protected
    @me
    def GET(self, id):
        form = users_delete()
        user = self.current_user()
        form.fill(id=user.id)
        return web.ctx.render.users_delete_complete(user=self.current_user(),
                users_delete=form)

    @protected
    @me
    def POST(self, id):
        u = self.current_user()
        u.deleted = True
        web.ctx.orm.add(u)
        logout()
        return jsonify(success=True)
