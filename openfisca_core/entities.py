# -*- coding: utf-8 -*-

from enumerations import Enum


class Entity(object):
    key = None
    plural = None
    label = None
    roles = None
    is_person = False

    @classmethod
    def get_role_enum(cls):
        return Enum(map(lambda role: role['key'], cls.roles))


    def __init__(self, simulation):
        self.simulation = simulation
        self.entity = self.__class__



    def __getattr__(self, attribute):
        entity = self.simulation.entities.get(attribute)
        if entity:
            return entity
        else:
            raise AttributeError(attribute)

    @property
    def members(self):
        return self.simulation.entities[self.simulation.tax_benefit_system.person_entity.key]


    def calculate(self, variable_name, period):
        if not (self.simulation.get_variable_entity(variable_name) == self.entity):
            variable_entity = self.simulation.get_variable_entity(variable_name)
            raise Exception(
                "Variable {} is not defined for {} but for {}".format(
                    variable_name, self.entity.label, variable_entity.label)
                )

        return self.simulation.calculate(variable_name, period)

    def calculate_add(self, variable_name, period):
        return self.simulation.calculate_add(variable_name, period)

    def calculate_divide(self, variable_name, period):
        return self.simulation.calculate_divide(variable_name, period)

    def sum(self, array, role = None):
        return self.simulation.sum_in_entity(array, self.entity, role = role)

    def project(self, array, role = None):
        return self.simulation.project_on_persons(array, self.entity, role = role)
