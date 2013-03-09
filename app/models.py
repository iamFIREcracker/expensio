#!/usr/bin/env python

import uuid
import json
from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import String

from app.database import Base


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__serializable__'):
            fields = {}
            for (field, f) in obj.__serializable__.iteritems():
                data = f(obj);

                try:
                    json.dumps(data)
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            return fields
        return json.JSONEncoder.default(self, obj)


def _uuid():
    return unicode(uuid.uuid4())


class User(Base):
    __tablename__ = 'user'

    id = Column(String, default=_uuid, primary_key=True)
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

def expenseid(context):
    return context.current_parameters['id']


class Expense(Base):
    __tablename__ = 'expense'

    id = Column(String, default=_uuid, primary_key=True)
    original_id = Column(String, ForeignKey('expense.id'), default=expenseid)
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
