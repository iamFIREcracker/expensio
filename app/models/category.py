#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.schema import UniqueConstraint

from app.models import uuid
from app.database import Base


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
