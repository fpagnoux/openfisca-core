# -*- coding: utf-8 -*-


class Entity(object):

    def __init__(self, key, label = u"", roles = {}, is_person = False):
        self.key = key
        self.label = label
        self.roles = roles
        self.is_person = is_person

    def iter_member_persons_role_and_id(self, member):
        # one by one, yield individu_role, individu_id
        role_index = 0
        for role in self.roles:
            individus = member[role]
            for individu in individus:
                yield role_index, individu
            role_index += 1
