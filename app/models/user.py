#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from app.models import uuid
from app.database import Base

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import String


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

