#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import String

from app.database import Base
from app.models import current_object_id
from app.models import uuid


class Expense(Base):
    __tablename__ = 'expense'

    id = Column(String, default=uuid, primary_key=True)
    original_id = Column(String, ForeignKey('expense.id'),
            default=current_object_id)
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


