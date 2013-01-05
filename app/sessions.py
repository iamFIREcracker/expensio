#!/usr/bin/env python

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Time
from sqlalchemy.ext.declarative import declarative_base

from config import DATABASE_SESSION_ENGINE


engine = create_engine(DATABASE_SESSION_ENGINE, echo=True)



Base = declarative_base()


class Session(Base):
    __tablename__ = 'session'

    session_id = Column(String, primary_key=True)
    atime = Column(Time, default=datetime.now)
    data = Column(Text)



metadata = Base.metadata


if __name__ == "__main__":
    metadata.create_all(engine)

