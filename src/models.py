#!/usr/bin/env python

import uuid
import json
from datetime import datetime

import web
from sqlalchemy import create_engine
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base

from config import DATE_FORMAT


if web.config.debug:
    engine = create_engine('sqlite:///mytestdatabase.db', echo=True)
else:
    engine = create_engine('sqlite:///mydatabase.db', echo=True)



Base = declarative_base()


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
    name = Column(String, nullable=False)
    google_id = Column(String)
    facebook_id = Column(String)
    twitter_id = Column(String)


class Expense(Base):
    __tablename__ = 'expense'

    id = Column(String, default=_uuid, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = Column(Integer, ForeignKey('user.id'))
    date = Column(DateTime, nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    note = Column(String)
    deleted = Column(Boolean, default=False, nullable=False)

    __serializable__ = {
            'id': lambda o: o.id,
            'date': lambda o: datetime.strftime(o.date, DATE_FORMAT),
            'created': lambda o: datetime.strftime(o.created, DATE_FORMAT),
            'updated': lambda o: datetime.strftime(o.updated, DATE_FORMAT),
            'category': lambda o: o.category,
            'amount': lambda o: float(o.amount),
            'currency': lambda o: '&euro;', # XXX use proper value
            'note': lambda o: o.note,
            'deleted': lambda o: bool(o.deleted),
            }



metadata = Base.metadata


if __name__ == "__main__":
    metadata.create_all(engine)
