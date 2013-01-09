#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .auth import LoginGoogleHandler
from .auth import LoginGoogleAuthorizedHandler
from .auth import LoginFacebookHandler
from .auth import LoginFacebookAuthorizedHandler
from .auth import LoginTwitterHandler
from .auth import LoginTwitterAuthorizedHandler
from .auth import LoginFakeHandler
from .auth import LoginFakeAuthorizedHandler
from .controllers.general import LogoutHandler
from .controllers.general import MainHandler
from .categories import CategoriesHandler
from .days import DaysHandler
from .expenses import ExpensesHandler
from .expenses import ExpensesAddHandler
from .expenses import ExpensesEditHandler
from .expenses import ExpensesDeleteHandler
from .expenses import ExpensesImportHandler
from .users import UsersEditHandler


URLS = (
    '/', MainHandler,

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
