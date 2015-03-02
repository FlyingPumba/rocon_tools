#
# License: BSD
#   https://raw.github.com/robotics-in-concert/rocon_tools/license/LICENSE
#
##############################################################################
# Description
##############################################################################

"""
.. module:: users_table
   :platform: Unix
   :synopsis: A database of users.


This module provides a class that acts as a database (dictionary style) of
some set of users.

----

"""
##############################################################################
# Imports
##############################################################################

import rocon_console.console as console
import rocon_uri

from . import interactions
from .exceptions import InvalidInteraction

##############################################################################
# Classes
##############################################################################


class UsersTable(object):
    '''
      The runtime populated users table along with methods to
      manipulate it.

      .. include:: weblinks.rst
    '''
    __slots__ = [
        '_users',  # rocon_interactions.interactions.User[]
    ]

    def __init__(self):
        """
        Constructs an empty users table.

        """
        self._users = []

    def users(self):
        '''
          List all roles for the currently stored users.

          :returns: a list of all roles
          :rtype: str[]
        '''
        # uniquify the list
        return list(set([i.name for i in self._users]))

    def roles(self, user=None):
        '''
          List all roles for the currently stored users.

          :returns: a list of all roles
          :rtype: str[]
        '''
        # uniquify the list
        if user:
             return list(set([i.role for i in self._users if i.name == user]))
        else:
            return list(set([i.role for i in self._users]))

    def __len__(self):
        return len(self._users)

    def __str__(self):
        """
        Convenient string representation of the table.
        """
#        s = ''
#        role_view = self.generate_role_view()
#        for role, users in role_view.iteritems():
#            s += console.bold + role + console.reset + '\n'
#            for user in users:
#                s += "\n".join("  " + i for i in str(user).splitlines()) + '\n'
        return "User and roles beign printed"

# TODO: change this to proper generate role view for Users table
    def generate_role_view(self):
        '''
          Creates a temporary copy of the users and sorts them into a dictionary
          view classified by role.

          :returns: A role based view of the users
          :rtype: dict { role(str) : :class:`.interactions.Interaction`[] }
        '''
        # there's got to be a faster way of doing this.
        users = list(self._users)
        role_view = {}
        for user in users:
            if user.role not in role_view.keys():
                role_view[user.role] = []
            role_view[user.role].append(user)
        return role_view

    def filter(self, roles=None, compatibility_uri='rocon:/'):
        '''
          Filter the users in the table according to role and/or compatibility uri.

          :param roles: a list of roles to filter against, use all roles if None
          :type roles: str []
          :param str compatibility_uri: compatibility rocon_uri_, eliminates users that don't match this uri.

          :returns users: subset of all users that survived the filter
          :rtype: :class:`.Interaction` []

          :raises: rocon_uri.RoconURIValueError if provided compatibility_uri is invalid.
        '''
        if roles:   # works for classifying non-empty list vs either of None or empty list
            role_filtered_users = [i for i in self._users if i.role in roles]
        else:
            role_filtered_users = list(self._users)
        filtered_users = [i for i in role_filtered_users
                                 if rocon_uri.is_compatible(i.compatibility, compatibility_uri)]
        return filtered_users

    def load(self, msgs):
        '''
          Load some users into the users table. This involves some initialisation
          and validation steps.

          :param msgs: a list of user specifications to populate the table with.
          :type msgs: rocon_interaction_msgs.User_ []
          :returns: list of all additions and any that were flagged as invalid
          :rtype: (:class:`.User` [], rocon_interaction_msgs.User_ []) : (new, invalid)
        '''
        new = []
        invalid = []
        for msg in msgs:
            try:
                user = interactions.User(msg)
                self._users.append(user)
                self._users = list(set(self._users))  # uniquify the list, just in case
                new.append(user)
            except InvalidInteraction:
                invalid.append(msg)
        return new, invalid

    def unload(self, msgs):
        '''
          Removed the specified users users table. This list is typically
          the same list as the user might initially send - no hashes yet generated.

          :param msgs: a list of users
          :type msgs: rocon_interaction_msgs.Interaction_ []

          :returns: a list of removed users
          :rtype: rocon_interaction_msgs.Interaction_ []
        '''
        removed = []
        for msg in msgs:
            msg_hash = interactions.generate_hash(msg.display_name, msg.role, msg.namespace)
            found = self.find(msg_hash)
            if found is not None:
                removed.append(msg)
                self._users.remove(found)
        return removed
