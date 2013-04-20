#!/usr/bin/env python

from uuid import uuid4
from datetime import datetime

import web
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.schema import UniqueConstraint

import app.config as config
from app.database import Base


def uuid():
    """Generates a ``uuid``."""
    return unicode(uuid4())


def current_object_id(context):
    """Returns the ``id`` of the current object to be stored."""
    return context.current_parameters['id']



class User(Base):
    __tablename__ = 'user'

    id = Column(String, default=uuid, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    avatar = Column(String)
    name = Column(String, nullable=False)
    currency = Column(String)
    google_id = Column(String)
    facebook_id = Column(String)
    twitter_id = Column(String)
    deleted = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % (self.name)


class Expense(Base):
    __tablename__ = 'expense'

    id = Column(String, default=uuid, primary_key=True)
    original_id = Column(String, ForeignKey('expense.id'),
            default=current_object_id)
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = Column(String, ForeignKey('user.id'))
    date = Column(DateTime, nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    note = Column(String)
    deleted = Column(Boolean, default=False, nullable=False)
    attachment = Column(String)

    def __repr__(self):
        return '<Expense %s, %r, %r, %f, %r, %r, %r>' % (self.date,
                                                         self.category,
                                                         self.note,
                                                         self.amount,
                                                         self.deleted,
                                                         self.created,
                                                         self.updated)


class Category(Base):
    __tablename__ = 'category'

    id = Column(String, default=uuid, primary_key=True)
    user_id = Column(String, ForeignKey('user.id'))
    name = Column(String, nullable=False)
    foreground = Column(String, nullable=False)
    background = Column(String, nullable=False)
    deleted = Column(Boolean, default=False, nullable=False)
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (UniqueConstraint('user_id', 'name', name='user_cname_uc'),
                     )

    def __repr__(self):
        return '<Category %r, %r, %r, %r, %r, %r>' % (self.id,
                                                      self.user_id,
                                                      self.name,
                                                      self.foreground,
                                                      self.background,
                                                      self.deleted)

    @staticmethod
    def exists(category_name, user_id):
        """Returns True if a category with name ``category_name`` and
        associated with the user ID ``user_id`` is already present in the
        system, False otherwise.
        """
        c = (web.ctx.orm.query(Category)
                .filter_by(user_id=user_id)
                .filter_by(name=category_name)
                .first())
        return c is not None

    @staticmethod
    def new(category_name, user_id):
        """Creates a new category with name ``category_name`` and associated
        with the user ID ``user_id``.
        """
        return Category(
                user_id=user_id, name=category_name,
                foreground=config.CATEGORY_FOREGROUND,
                background=config.CATEGORY_BACKGROUND)
