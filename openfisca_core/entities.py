# -*- coding: utf-8 -*-

import numpy as np
import warnings

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
        self.members_entity_id = None
        self.members_role = None
        self.members_legacy_role = None
        self.members_position = None

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

    def calculate(self, variable_name, period = None):
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

    #  Aggregation persons -> entity

    def sum(self, array, role = None):

        result = self.empty_array()
        if role is not None:
            role_filter = (self.members_role == role)

            # Entities for which one person at least has the given role
            entity_has_role_filter = np.bincount(self.members_entity_id, weights = role_filter) > 0

            result[entity_has_role_filter] += np.bincount(self.members_entity_id[role_filter], weights = array[role_filter])
        else:
            result += np.bincount(self.members_entity_id, weights = array)
        return result

    def any(self, array, role = None):
        sum_in_entity = self.sum(array, role = role)
        return (sum_in_entity > 0)

    def reduce(self, array, reducer, neutral_element, role = None):
        position_in_entity = self.members_position
        role_in_entity = self.members_role
        role_filter = (role_in_entity == role) if role is not None else True

        result = self.filled_array(neutral_element)  # Neutral value that will be returned if no one with the given role exists.

        # We loop over the positions in the entity
        # Looping over the entities is tempting, but potentielly slow if there are a lot of entities
        nb_positions = np.max(position_in_entity) + 1
        for p in range(nb_positions):
            filter = (position_in_entity == p) * role_filter
            entity_filter = self.any(filter)
            result[entity_filter] = reducer(result[entity_filter], array[filter])

        return result

    def all(self, array, role = None):
        return self.reduce(array, neutral_element = True, reducer = np.logical_and, role = role)

    def max(self, array, role = None):
        return self.reduce(array, neutral_element = - np.infty, reducer = np.maximum, role = role)

    def min(self, array, role = None):
        return self.reduce(array, neutral_element = np.infty, reducer = np.minimum, role = role)

    def nb_persons(self, role = None):
            role_condition = (self.members_role == role)
            return self.sum(role_condition)

    # Projection person -> entity

    def value_from_person(self, array, role, default = 0):
        # TODO: Make sure the role is unique
        result = self.filled_array(default)
        role_filter = (self.members_role == role)
        entity_filter = self.any_in_entity(role_filter)

        result[entity_filter] = array[role_filter]

        return result

    # Projection entity -> person(s)

    def project(self, array, role = None):
        role_condition = (self.members_role == role) if role is not None else True
        return array[self.members_entity_id] * role_condition

    def project_on_first_person(self, array):
        entity_position_array = self.members_position
        entity_index_array = self.members_entity_id
        boolean_filter = (entity_position_array == 0)
        return array[entity_index_array] * boolean_filter

    def share_between_members(self, array, role = None):
        nb_persons_per_entity = self.nb_persons(role)
        return self.project(array / nb_persons_per_entity, role = role)

    # Projection person -> person

    def swap(self, array, role):
        # Make sure there is only two people with the role
        entity_filter = self.nb_persons(role) == 2
        higher_value = entity_filter * self.max(array, role)
        lower_value = entity_filter * self.min(array, role)
        higher_value_i = self.project(higher_value, role)
        lower_value_i = self.project(lower_value, role)
        return (array == higher_value_i) * lower_value_i + (array == lower_value_i) * higher_value_i

    # Projection entity -> entity

    def transpose_to_entity(self, array, target_entity, origin_entity):
        input_projected = self.project_on_first_person(array, entity = origin_entity)
        return self.sum_in_entity(input_projected, entity = target_entity)

    # Helpers

    def empty_array(self):
        return np.zeros(self.count)

    def filled_array(self, value):
        with warnings.catch_warnings():  # Avoid a non-relevant warning
            warnings.simplefilter("ignore")
            return np.full(self.count, value)
