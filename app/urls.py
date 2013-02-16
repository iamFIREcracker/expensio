#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .controllers.auth import LoginFacebookAuthorizedHandler
from .controllers.auth import LoginFacebookHandler
from .controllers.auth import LoginFakeAuthorizedHandler
from .controllers.auth import LoginFakeHandler
from .controllers.auth import LoginGoogleAuthorizedHandler
from .controllers.auth import LoginGoogleHandler
from .controllers.auth import LoginTwitterAuthorizedHandler
from .controllers.auth import LoginTwitterHandler
from .controllers.categories import CategoriesNamesHandler
from .controllers.expenses import ExpensesAddHandler
from .controllers.expenses import ExpensesDeleteHandler
from .controllers.expenses import ExpensesEditHandler
from .controllers.expenses import ExpensesHandler
from .controllers.expenses import ExpensesExportHandler
from .controllers.expenses import ExpensesExportTSVStatusHandler
from .controllers.expenses import ExpensesImportHandler
from .controllers.general import LogoutHandler
from .controllers.general import MainHandler
from .controllers.stats import StatsCategoriesHandler
from .controllers.stats import StatsDaysHandler
from .controllers.users import UsersAvatarUploadChange
from .controllers.users import UsersAvatarUploadChangeStatusHandler
from .controllers.users import UsersAvatarUploadRemove
from .controllers.users import UsersDeleteHandler
from .controllers.users import UsersEditHandler
from .controllers.users import UsersProfileHandler


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

    '/users/(.+)/profile', UsersProfileHandler,
    '/users/(.+)/edit', UsersEditHandler,
    '/users/(.+)/avatar/change', UsersAvatarUploadChange,
    '/users/(.+)/avatar/change/status/(.+)', UsersAvatarUploadChangeStatusHandler,
    '/users/(.+)/avatar/remove', UsersAvatarUploadRemove,
    '/users/(.+)/delete', UsersDeleteHandler,

    '/stats/days', StatsDaysHandler,
    '/stats/categories', StatsCategoriesHandler,

    '/expenses', ExpensesHandler,
    '/expenses/add', ExpensesAddHandler,
    '/expenses/(.+)/edit', ExpensesEditHandler,
    '/expenses/(.+)/delete', ExpensesDeleteHandler,
    '/expenses/import', ExpensesImportHandler,
    '/expenses/export', ExpensesExportHandler,
    '/expenses/export/tsv/status/(.+)', ExpensesExportTSVStatusHandler,

    '/categories/names', CategoriesNamesHandler,
)
