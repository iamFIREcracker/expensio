#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import Counter

import web

import sqlalchemy
from PIL import Image

import app.config as config
import app.formatters as formatters
import app.lib.fs as fs
import app.lib.logging as logging
import app.lib.media as media
import app.lib.users as users
from app.celery import celery
from app.database import create_session
from app.exceptions import ResponseContent
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
    logger = logging.LoggingSubscriber(create_logger(web.config))
    thumbnailer = media.ThumbnailGenerator()
    mediamapper = media.MediaContentMapper(mediadir)
    fsadapter = fs.FileSystemAdapter()
    urlgenerator = media.MediaURLGenerator(mediadir, baseurl)
    avatarchanger = users.AvatarUpdater(Users)

    def thumbnail_maker(sourcepath, destinationpath, size):
        img = Image.open(sourcepath)
        img.thumbnail(size, Image.ANTIALIAS)
        img.save(destinationpath)

    class ThumbnailsReadySubscriber(object):
        def thumbnails_ready(self, *thumbnails):
            mediamapper.perform(*thumbnails)

    class MediaPathsReadySubscriber(object):
        def mediapaths_ready(self, *mappings):
            fsadapter.rename(*mappings)

    class FilesRenamedSubscriber(object):
        def files_renamed(self, (tmppath, mediapath)):
            urlgenerator.perform(mediapath)

    class MediaURLsSubscriber(object):
        def invalid_paths(self, *paths):
            message = 'Cannot generate media URLs for paths:  %(paths)r'
            message = message % dict(paths=paths)
            raise ValueError(message)
        def urls_ready(self, avatar):
            avatarchanger.perform(userid, avatar)

    class AvatarUpdaterSubscriber(object):
        def not_existing_user(self, user_id):
            message = 'Invalid user ID: %(id)s' % dict(id=user_id)
            raise ValueError(message)
        def avatar_updated(self, avatar):
            raise ResponseContent(avatar)

    thumbnailer.add_subscriber(logger, ThumbnailsReadySubscriber())
    mediamapper.add_subscriber(logger, MediaPathsReadySubscriber())
    fsadapter.add_subscriber(logger, FilesRenamedSubscriber())
    urlgenerator.add_subscriber(logger, MediaURLsSubscriber())
    avatarchanger.add_subscriber(logger, AvatarUpdaterSubscriber())
    try:
        thumbnailer.perform(thumbnail_maker, tempfile, (128, 128))
    except ResponseContent as r:
        return r.content


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
