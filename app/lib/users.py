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
            self.publish('avatar_updated', avatar)
        else:
            self.publish('not_existing_user', user_id)
