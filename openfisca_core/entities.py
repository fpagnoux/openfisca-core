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
        role_index = 0
        for role in self.roles:
            role_name = role['key']
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
                        role_index += 1
                else:
                    for individu in individus:
                        yield index_in_entity, role_index, individu
                        index_in_entity += 1
            role_index += 1

    def get_role_enum(self):
        return Enum(map(lambda role: role['key'], self.roles))
