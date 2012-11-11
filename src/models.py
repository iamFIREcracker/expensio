#!/usr/bin/env python

import json
from datetime import datetime

import web
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta

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


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    updated = Column(DateTime)
    name = Column(String, nullable=False)
    access_token = Column(String, nullable=False)


class Expense(Base):
    __tablename__ = 'expense'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    date = Column(DateTime)
    category = Column(String, nullable=False)
    amount = Column(Float)
    note = Column(String)

    __serializable__ = {
            'id': lambda o: int(o.id),
            'date': lambda o: datetime.strftime(o.date, DATE_FORMAT),
            'created': lambda o: datetime.strftime(o.created, DATE_FORMAT),
            'updated': lambda o: datetime.strftime(o.updated, DATE_FORMAT),
            'category': lambda o: o.category,
            'amount': lambda o: float(o.amount),
            'currency': lambda o: '&euro;',
            'note': lambda o: o.note,
            }



metadata = Base.metadata


if __name__ == "__main__":
    metadata.create_all(engine)
