# -*- coding: utf-8 -*-

from enumerations import Enum


class Entity(object):

    def __init__(self, key, label = u"", roles = {}, is_person = False):
        self.key = key
        self.label = label
        self.is_person = is_person
        self.roles = roles

    def iter_member_persons_role_and_id(self, member):
        # One by one, yield individu_position, individu_role, individu_id
        index_in_entity = 0
        role_index = 0
        role_in_scenario_indexes = {}

        for role in self.roles:
            if role.get('role_in_scenario'):
                role_name = role['role_in_scenario']
                index = role_in_scenario_indexes.get(role_name) or 0
                role_in_scenario_indexes[role_name] = index + 1
                individus = (len(member[role_name]) > index) and member[role_name][index]
            else:
                role_name = role['key']
                individus = member[role_name]

            if individus:
                if type(individus) == str:
                    individus = [individus]

                for individu in individus:
                    yield index_in_entity, role_index, individu
                    index_in_entity += 1
            role_index += 1

    def get_role_enum(self):
        return Enum(map(lambda role: role['key'], self.roles))
