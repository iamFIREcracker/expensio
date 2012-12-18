#!/usr/bin/env python

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Time
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('sqlite:///sessions.db', echo=True)



Base = declarative_base()


class Session(Base):
    __tablename__ = 'session'

    session_id = Column(String, primary_key=True)
    atime = Column(Time, default=datetime.now)
    data = Column(Text)



metadata = Base.metadata


if __name__ == "__main__":
    metadata.create_all(engine)

