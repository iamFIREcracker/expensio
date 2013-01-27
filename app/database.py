#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app import config

engine = create_engine(config.DATABASE_URL, convert_unicode=True, echo=True)
db_session = scoped_session(sessionmaker(#autocommit=False,
                                         #autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import app.models
    import app.sessions
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    init_db()
