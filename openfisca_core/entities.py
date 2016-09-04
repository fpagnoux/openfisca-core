# -*- coding: utf-8 -*-

from enumerations import Enum


class Entity(object):
    key = None
    label = None
    roles = None
    is_person = False

    @classmethod
    def get_role_enum(cls):
        return Enum(map(lambda role: role['key'], cls.roles))


    def __init__(self, simulation):
        self.simulation = simulation

    def calculate(self, variable_name, period):
        return self.simulation.calculate(variable_name, period)
