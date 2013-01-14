#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .controllers.auth import LoginGoogleHandler
from .controllers.auth import LoginGoogleAuthorizedHandler
from .controllers.auth import LoginFacebookHandler
from .controllers.auth import LoginFacebookAuthorizedHandler
from .controllers.auth import LoginTwitterHandler
from .controllers.auth import LoginTwitterAuthorizedHandler
from .controllers.auth import LoginFakeHandler
from .controllers.auth import LoginFakeAuthorizedHandler
from .controllers.categories import CategoriesHandler
from .controllers.days import DaysHandler
from .controllers.expenses import ExpensesHandler
from .controllers.expenses import ExpensesAddHandler
from .controllers.expenses import ExpensesEditHandler
from .controllers.expenses import ExpensesDeleteHandler
from .controllers.expenses import ExpensesImportHandler
from .controllers.general import LogoutHandler
from .controllers.general import MainHandler
from .controllers.users import UsersEditHandler


URLS = (
    '/', MainHandler,
    '/(\d+)/(\d+)', MainHandler,

    '/login/google', LoginGoogleHandler,
    '/login/google/authorized', LoginGoogleAuthorizedHandler,
    '/login/facebook', LoginFacebookHandler,
    '/login/facebook/authorized', LoginFacebookAuthorizedHandler,
    '/login/twitter', LoginTwitterHandler,
    '/login/twitter/authorized', LoginTwitterAuthorizedHandler,
    '/login/fake', LoginFakeHandler,
    '/login/fake/authorized', LoginFakeAuthorizedHandler,
    '/logout', LogoutHandler,

    '/users/(.+)/edit', UsersEditHandler,

    '/days.json', DaysHandler,

    '/categories.json', CategoriesHandler,

    '/expenses.json', ExpensesHandler,
    '/expenses/add', ExpensesAddHandler,
    '/expenses/(.+)/edit', ExpensesEditHandler,
    '/expenses/(.+)/delete', ExpensesDeleteHandler,
    '/expenses/import', ExpensesImportHandler,
)
