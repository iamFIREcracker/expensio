#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app.lib.publisher import Publisher


class AvatarUpdater(Publisher):
    """
    >>> this = AvatarUpdater()
    >>> class Subscriber(object):
    ...   def not_existing_user(self, user_id):
    ...     print 'Invalid user'
    ...   def avatar_updated(self, avatar):
    ...     print 'Avatar updated'
    >>> this.add_subscriber(Subscriber())
    >>> class Repository(object):
    ...   @staticmethod
    ...   def change_avatar(user_id, avatar):
    ...     if user_id == 'invalid':
    ...       return False
    ...     else:
    ...       return True
    >>> repo = Repository()


    >>> this.perform(repo, 'invalid', None)
    Invalid user

    >>> this.perform(repo, 'valid', 'http://localhost/avatar.png')
    Avatar updated
    """
    def perform(self, repository, user_id, avatar):
        """Updates the avatar of the user identified by ``user_id``.

        If no user exists with the specified ID, a 'not_existing_user' message
        is published, followed by the the user ID.

        On the other hand, a 'avatar_updated' message is published if the user
        exists and the avatar is updated successfully.
        """
        if repository.change_avatar(user_id, avatar):
            self.publish('avatar_updated', user_id, avatar)
        else:
            self.publish('not_existing_user', user_id)


class UserUpdater(Publisher):
    """
    >>> this = UserUpdater()
    >>> class Subscriber(object):
    ...   def not_existing_user(self, user_id):
    ...     print 'Invalid user'
    ...   def user_updated(self, name, currency):
    ...     print 'User updated'
    >>> this.add_subscriber(Subscriber())
    >>> class Repository(object):
    ...   @staticmethod
    ...   def update(user_id, name, currency):
    ...     if user_id == 'invalid':
    ...       return False
    ...     else:
    ...       return True
    >>> repo = Repository()


    >>> this.perform(repo, 'invalid', None, None)
    Invalid user

    >>> this.perform(repo, 'valid', 'John Smith', '$')
    User updated
    """

    def perform(self, repository, user_id, name, currency):
        """Sets the 'name' and the 'currency' fields of the specified user.

        If no user exists with the specified ID, a 'not_existing_user' message
        is published, followed by the user ID.

        On the other hand, a 'user_updated' message is published if the user
        exists and the fields have been updated successfully.
        """
        if repository.update(user_id, name, currency):
            self.publish('user_updated', user_id, name, currency)
        else:
            self.publish('not_existing_user', user_id)


class UserDeleter(Publisher):
    """
    >>> this = UserDeleter()
    >>> class Subscriber(object):
    ...   def not_existing_user(self, user_id):
    ...     print 'Invalid user'
    ...   def user_deleted(self):
    ...     print 'User deleted'
    >>> this.add_subscriber(Subscriber())
    >>> class Repository(object):
    ...   @staticmethod
    ...   def delete(user_id):
    ...     if user_id == 'invalid':
    ...       return False
    ...     else:
    ...       return True
    >>> repo = Repository()


    >>> this.perform(repo, 'invalid')
    Invalid user

    >>> this.perform(repo, 'valid')
    User deleted
    """

    def perform(self, repository, user_id):
        """Delete the user identified by ``user_id``.

        If no user exists with the specified ID, a 'not_existing_user' message
        is published, followed by the user ID.

        On the other hand, a 'user_deleted' message is published if the user
        exists and the fields have been deleted successfully.
        """
        if repository.delete(user_id):
            self.publish('user_deleted', user_id)
        else:
            self.publish('not_existing_user', user_id)
