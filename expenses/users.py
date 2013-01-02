#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web

from forms import users_edit
from utils import applicationinitializer
from utils import me
from utils import protected
from utils import BaseHandler


urls = (
    '/users/(.+)/edit', 'UsersEditHandler',
)

application = web.application(urls, globals())
applicationinitializer(application)



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


if __name__ == '__main__':
    application.run()
