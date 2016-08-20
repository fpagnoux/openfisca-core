# -*- coding: utf-8 -*-


from .tools import empty_clone


class Entity(object):
    # count = 0
    # roles_count = None
#
    def __init__(self, key, label = u"", roles = {}, is_person = False):
        self.key = key
        self.label = label
        self.roles = roles
        self.is_person = is_person
        pass

    def iter_member_persons_role_and_id(self, member):
        for role in roles:

