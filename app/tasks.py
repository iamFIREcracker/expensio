#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from collections import Counter

import sqlalchemy
from PIL import Image

import app.config as config
import app.formatters as formatters
from app.celery import celery
from app.database import db_session
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


@celery.task
def ExpensesExportTSVTask(exportman, user):
    filename = 'expenses.tsv'
    expenses = (db_session.query(Expense)
                .filter_by(user_id=user.id)
                .filter(Expense.deleted == False)
                .order_by(Expense.date.desc())
                .all())
    return exportman.add(user.id, filename,
            (ExpenseTSVWrapper(e) for e in expenses))


@celery.task
def UsersAvatarChangeTask(avatar, avatarman, user, home):
    _, ext = os.path.splitext(avatar.filename)
    im = Image.open(avatar.name)
    im.thumbnail((128, 128), Image.ANTIALIAS)
    im.save(avatar.name)

    url = avatarman.add(avatar) if avatar else None

    user.avatar = url
    db_session.add(user)
    db_session.commit()
    db_session.remove()

    return os.path.join(home, url)


@celery.task
def CategoriesResetTask(user):
    def key(*args):
        return ''.join(args)

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
