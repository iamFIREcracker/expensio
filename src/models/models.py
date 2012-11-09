#!/usr/bin/env python

import json

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String


engine = create_engine('sqlite:///mydatabase.db', echo=True)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta


Base = declarative_base()


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for (field, f) in obj.__serializable__.iteritems():
                data = f(obj.__getattribute__(field)) if hasattr(obj, field) else f()

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
    created = Column(DateTime)
    updated = Column(DateTime)
    date = Column(DateTime)
    category = Column(String, nullable=False)
    amount = Column(Float)
    note = Column(String)

    __serializable__ = {
            'id': str,
            'date': str,
            'category': str,
            'amount': float,
            'currency': lambda: '&euro;',
            'note': str,
            }


metadata = Base.metadata


if __name__ == "__main__":
    metadata.create_all(engine)
