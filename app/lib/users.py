#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app.lib.publisher import Publisher


class AvatarUpdater(Publisher):
    """

    >>> class Session(object):
    ...   def commit(self):
    ...     print 'Commit session'
    ...   def merge(self, user):
    ...     print 'Merge user'
    ...     return user
    >>> class Repository(object):
    ...   @staticmethod
    ...   def get(user_id):
    ...     class User(object):
    ...       avatar = None
    ...       session = Session()
    ...     if user_id == 'invalid':
    ...       return None
    ...     else:
    ...       return User()
    >>> this = AvatarUpdater(Repository())
    >>> class Subscriber(object):
    ...   def not_existing_user(self, user_id):
    ...     print 'Invalid user'
    ...   def avatar_updated(self, avatar):
    ...     print 'Avatar updated'
    >>> this.add_subscriber(Subscriber())


    >>> this.perform('invalid', None)
    Invalid user

    >>> this.perform('valid', 'http://localhost/avatar.png')
    Commit session
    Merge user
    Avatar updated
    """
    def __init__(self, repository):
        super(AvatarUpdater, self).__init__()
        self.repository = repository

    def perform(self, user_id, avatar):
        """Updates the avatar of the user identified by ``user_id``.

        If no user exists with the specified ID, a 'not_existing_user' message
        is published, followed by the the user ID.

        On the other hand, a 'avatar_updated' message is published if the user
        exists and the avatar is updated successfully.
        """
        user = self.repository.get(user_id)
        if user is None:
            self.publish('not_existing_user', user_id)
        else:
            user.avatar = avatar
            user.session.commit()
            user = user.session.merge(user)
            self.publish('avatar_updated', user.avatar)
