# -*- coding: utf-8 -*-

import numpy as np

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
        self.count = 0
        self.step_size = 0


    # To add when building the simulation

    def __getattr__(self, attribute):
        entity = self.simulation.entities.get(attribute)
        if entity:
            return entity
        else:
            raise AttributeError(attribute)

    @property
    def members(self):
        return self.simulation.entities[self.simulation.tax_benefit_system.person_entity.key]

    # Calulations

    def calculate(self, variable_name, period):
        if not (self.simulation.get_variable_entity(variable_name) == self):
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


    def get_entity_id(self):
        tbs = self.simulation.tax_benefit_system
        index_column_name = tbs.get_entity_index_column_name(self)
        return self.simulation.holder_by_name[index_column_name].array

    def get_role_in_entity(self, entity):
        tbs = self.tax_benefit_system
        role_column_name = tbs.get_entity_role_column_name(entity)
        return self.holder_by_name[role_column_name].array

    def get_legacy_role_in_entity(self, entity):
        tbs = self.tax_benefit_system
        legacy_role_column_name = tbs.get_entity_legacy_role_column_name(entity)
        return self.holder_by_name[legacy_role_column_name].array

    def get_position_in_entity(self, entity):
        tbs = self.tax_benefit_system
        position_column_name = tbs.get_entity_position_column_name(entity)
        return self.holder_by_name[position_column_name].array

    def transpose_to_entity(self, array, target_entity, origin_entity):
        input_projected = self.project_on_first_person(array, entity = origin_entity)
        return self.sum_in_entity(input_projected, entity = target_entity)

    #  Aggregation persons -> entity

    def sum(self, array, role = None):

        entity_index_array = self.get_entity_id()
        result = self.empty_array()
        if role is not None:
            entity_role_array = self.get_role_in_entity()
            role_filter = (entity_role_array == role)

            # Entities for which one person at least has the given role
            entity_has_role_filter = np.bincount(entity_index_array, weights = role_filter) > 0

            result[entity_has_role_filter] += np.bincount(entity_index_array[role_filter], weights = array[role_filter])
        else:
            result += np.bincount(entity_index_array, weights = array)
        return result

    def any_in_entity(self, array, entity, role = None):
        sum_in_entity = self.sum_in_entity(array, entity, role = role)
        return (sum_in_entity > 0)

    def reduce_in_entity(self, array, entity, reducer, neutral_element, role = None):
        position_in_entity = self.get_position_in_entity(entity)
        role_in_entity = self.get_role_in_entity(entity)
        role_filter = (role_in_entity == role) if role is not None else True

        result = self.filled_array(entity, neutral_element)  # Neutral value that will be returned if no one with the given role exists.

        # We loop over the positions in the entity
        # Looping over the entities is tempting, but potentielly slow if there are a lot of entities
        nb_positions = np.max(position_in_entity) + 1
        for p in range(nb_positions):
            filter = (position_in_entity == p) * role_filter
            entity_filter = self.any_in_entity(filter, entity)
            result[entity_filter] = reducer(result[entity_filter], array[filter])

        return result

    def all_in_entity(self, array, entity, role = None):

        return self.reduce_in_entity(array, entity, neutral_element = True, reducer = np.logical_and, role = role)

    def max_in_entity(self, array, entity, role = None):
        return self.reduce_in_entity(array, entity, neutral_element = - np.infty, reducer = np.maximum, role = role)

    def min_in_entity(self, array, entity, role = None):
        return self.reduce_in_entity(array, entity, neutral_element = np.infty, reducer = np.minimum, role = role)

    def nb_persons_in_entity(self, entity, role = None):
            role_condition = (self.get_role_in_entity(entity) == role)
            return self.sum_in_entity(role_condition, entity)

    # Projection person -> entity

    def value_from_person(self, array, entity, role, default = 0):
        # TODO: Make sure there is unique
        result = self.filled_array(entity, default)
        role_filter = (self.get_role_in_entity(entity) == role)
        entity_filter = self.any_in_entity(role_filter, entity)

        result[entity_filter] = array[role_filter]

        return result

    # Projection entity -> person(s)

    def project(self, array, role = None):
        role_condition = (self.get_role_in_entity(entity) == role) if role is not None else True
        entity_index_array = self.get_entity_id()
        return array[entity_index_array] * role_condition

    def project_on_first_person(self, array, entity):
        entity_position_array = self.get_position_in_entity(entity)
        entity_index_array = self.get_entity_id(entity)
        boolean_filter = (entity_position_array == 0)
        return array[entity_index_array] * boolean_filter

    def share_between_members(self, array, entity, role = None):
        nb_persons_per_entity = self.nb_persons_in_entity(entity, role)
        return self.project_on_persons(array / nb_persons_per_entity, entity, role = role)

    # Projection person -> person

    def swap_in_entity(self, array, entity, role):
        # Make sure there is only two people with the role
        entity_filter = self.nb_persons_in_entity(entity, role) == 2
        higher_value = entity_filter * self.max_in_entity(array, entity, role)
        lower_value = entity_filter * self.min_in_entity(array, entity, role)
        higher_value_i = self.project_on_persons(higher_value, entity, role)
        lower_value_i = self.project_on_persons(lower_value, entity, role)
        return (array == higher_value_i) * lower_value_i + (array == lower_value_i) * higher_value_i

    # Helpers

    def empty_array(self):
        return np.zeros(self.count)

    def filled_array(self, value):
        with warnings.catch_warnings():  # Avoid a non-relevant warning
            warnings.simplefilter("ignore")
            return np.full(self.count, value)
