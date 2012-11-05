#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String


engine = create_engine('sqlite:///mydatabase.db', echo=True)

from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


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


metadata = Base.metadata


if __name__ == "__main__":
    metadata.create_all(engine)
