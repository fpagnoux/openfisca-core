# -*- coding: utf-8 -*-

from enumerations import Enum


class Entity(object):

    def __init__(self, key, label = u"", roles = {}, is_person = False):
        self.key = key
        self.label = label
        self.roles = roles
        self.is_person = is_person

    def iter_member_persons_role_and_id(self, member):
        # one by one, yield individu_position, individu_role, individu_id
        index_in_entity = 0
        for role_name, role in self.roles.iteritems():
            individus = member[role_name]
            if individus is not None:
                if type(individus) == str:
                    individus = [individus]

                if role.get('subroles'):
                    subroles = role.get('subroles')
                    index_in_subrole = 0
                    for individu in individus:
                        yield index_in_entity, subroles[index_in_subrole], individu
                        index_in_subrole += 1
                else:
                    for individu in individus:
                        yield index_in_entity, role_name, individu
                        index_in_entity += 1

    def get_role_enum(self):
        return Enum(self.roles.keys())
