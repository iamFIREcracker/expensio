#!/usr/bin/env python
# -*- coding: utf-8 -*-

import app.config as config

from .controllers.auth.facebook import AccountsFacebookDisconnectHandler
from .controllers.auth.google import AccountsGoogleDisconnectHandler
from .controllers.auth.twitter import AccountsTwitterDisconnectHandler
from .controllers.auth.fake import AccountsFakeDisconnectHandler
from .controllers.auth.fake import AccountsFakePopulateHandler
from .controllers.auth import LoginFacebookAuthorizedHandler
from .controllers.auth import LoginFacebookHandler
from .controllers.auth import LoginFakeAuthorizedHandler
from .controllers.auth import LoginFakeHandler
from .controllers.auth import LoginGoogleAuthorizedHandler
from .controllers.auth import LoginGoogleHandler
from .controllers.auth import LoginTwitterAuthorizedHandler
from .controllers.auth import LoginTwitterHandler
from .controllers.categories import CategoriesHandler
from .controllers.categories import CategoriesEditHandler
from .controllers.categories import CategoriesResetHandler
from .controllers.categories import CategoriesResetStatusHandler
from .controllers.expenses import ExpensesAddHandler
from .controllers.expenses import ExpensesDeleteHandler
from .controllers.expenses import ExpensesEditHandler
from .controllers.expenses import ExpensesHandler
from .controllers.expenses import ExpensesExportHandler
from .controllers.expenses import ExpensesExportTSVStatusHandler
from .controllers.expenses import ExpensesImportHandler
from .controllers.general import ExportHandler
from .controllers.general import ImportHandler
from .controllers.general import LogoutHandler
from .controllers.general import MainHandler
from .controllers.general import StatsHandler
from .controllers.general import UsersDeactivateHandler
from .controllers.general import UsersProfileHandler
from .controllers.stats import StatsCategoriesHandler
from .controllers.stats import StatsDaysHandler
from .controllers.users import UsersAvatarChange
from .controllers.users import UsersAvatarChangeStatusHandler
from .controllers.users import UsersAvatarRemove
from .controllers.users import UsersDeleteHandler
from .controllers.users import UsersEditHandler


URLS = (
    '/login/google', LoginGoogleHandler,
    '/login/google/authorized', LoginGoogleAuthorizedHandler,
    '/accounts/google/disconnect', AccountsGoogleDisconnectHandler,
    '/login/facebook', LoginFacebookHandler,
    '/login/facebook/authorized', LoginFacebookAuthorizedHandler,
    '/accounts/facebook/disconnect', AccountsFacebookDisconnectHandler,
    '/login/twitter', LoginTwitterHandler,
    '/login/twitter/authorized', LoginTwitterAuthorizedHandler,
    '/accounts/twitter/disconnect', AccountsTwitterDisconnectHandler,
    '/logout', LogoutHandler,

    '/users/(.+)/edit', UsersEditHandler,
    '/users/(.+)/avatar/change', UsersAvatarChange,
    '/users/(.+)/avatar/change/status/(.+)', UsersAvatarChangeStatusHandler,
    '/users/(.+)/avatar/remove', UsersAvatarRemove,
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

    '/categories', CategoriesHandler,
    '/categories/(.+)/edit', CategoriesEditHandler,
    '/categories/reset', CategoriesResetHandler,
    '/categories/reset/status/(.+)', CategoriesResetStatusHandler,

    '/', MainHandler,
    '/(\d+)/(\d+)', MainHandler,
    '/profile', UsersProfileHandler,
    '/deactivate', UsersDeactivateHandler,
    '/import', ImportHandler,
    '/export', ExportHandler,
    '/stats/(quarter|year|life)', StatsHandler,
) + (() if not config.DEV else (
    # Develop routes
    '/login/fake', LoginFakeHandler,
    '/login/fake/authorized', LoginFakeAuthorizedHandler,
    '/accounts/fake/disconnect', AccountsFakeDisconnectHandler,
    '/accounts/fake/populate', AccountsFakePopulateHandler,
))
