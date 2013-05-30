#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import Counter
from functools import wraps

import sqlalchemy
import web
from PIL import Image

import app.config as config
import app.formatters as formatters
import app.lib.fs as fs
from app.workflows.users import change_avatar_task
from app.celery import celery
from app.database import create_session
from app.logging import create_logger
from app.managers import Users
from app.models import Base
from app.models import Category
from app.models import Expense
from app.models import User

class ExpenseTSVWrapper(object):

    def __init__(self, e):
        self.e = e

    def __repr__(self):
        date = formatters.date_us(self.e.date)
        category = self.e.category
        amount = "{:,.2f}".format(self.e.amount)
        note = self.e.note

        return '%s\n' % ('\t'.join([date, category, amount, note]), )


def automatic_session_remover(func):
    """Automatically closes any open session with the database."""
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            Base.session.remove()
    return inner


@celery.task
def ExpensesExportTSVTask(exportman, user):
    filename = 'expenses.tsv'
    db_session = create_session()
    expenses = (db_session.query(Expense)
                .filter_by(user_id=user.id)
                .filter(Expense.deleted == False)
                .order_by(Expense.date.desc())
                .all())
    return exportman.add(user.id, filename,
            (ExpenseTSVWrapper(e) for e in expenses))


@celery.task
@automatic_session_remover
def UsersAvatarChangeTask(userid, tempfile, mediadir, baseurl):
    def thumbnail_maker(sourcepath, destinationpath, size):
        img = Image.open(sourcepath)
        img.thumbnail(size, Image.ANTIALIAS)
        img.save(destinationpath)
    logger = create_logger(web.config)
    fsadapter = fs.FileSystemAdapter()
    return change_avatar_task(logger, tempfile, thumbnail_maker, mediadir,
                              fsadapter, baseurl, Users, userid)

@celery.task
def CategoriesResetTask(user):
    def key(*args):
        return ''.join(args)

    db_session = create_session()
    user_categories_counter = Counter()
    user_categories = set()

    expenses = (db_session.query(Expense, User).join(User)
                    .filter(Expense.user_id == user.id)
                    .filter(User.deleted == False)
                    .order_by(Expense.created.asc()))
    categories = []
    for expense, user in expenses:
        k = key(expense.user_id, expense.category)
        if k not in user_categories:
            color = config.CATEGORY_PALETTE[user_categories_counter[user.id]]

            category = Category(user_id=expense.user_id,
                                name=expense.category,
                                foreground=color['foreground'],
                                background=color['background'])
            db_session.add(category)
            try:
                db_session.commit()
                categories.append(category)
            except sqlalchemy.exc.IntegrityError:
                db_session.rollback()

                category = (db_session.query(Category)
                                .filter_by(user_id=user.id)
                                .filter_by(name=expense.category)
                                .first())
                category.foreground = color['foreground']
                category.background = color['background']

                db_session.add(category)
                db_session.commit()
                categories.append(category)

            user_categories.add(k)
            user_categories_counter[expense.user_id] += 1

    db_session.remove()
    return categories
