# -*- coding: utf-8 -*-

from enumerations import Enum


class Entity(object):

    def __init__(self, key, label = u"", roles = {}, is_person = False):
        self.key = key
        self.label = label
        self.is_person = is_person
        self.roles = roles

    def get_role_enum(self):
        return Enum(map(lambda role: role['key'], self.roles))
