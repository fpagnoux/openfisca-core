# -*- coding: utf-8 -*-

from openfisca_core.tools import assert_near
from nose.tools import assert_equals

from .test_entities import UNORDERED_TEST_CASE, new_simulation, MONTH

def test_existence_matrix():
    simulation = new_simulation(UNORDERED_TEST_CASE, MONTH)
    members = simulation.household.members
    existence_matrix = members.existence_matrix

    assert_near(existence_matrix.sum(0), [4, 2])  # 4 persons in the 1st entity, 2 in the second
    assert_equals(existence_matrix[2,1], False)  # The 3rd person does not exist in the 2nd entity
    assert_equals(existence_matrix[3,1], False)  # The 4th person does not exist in the 2nd entity


def test_call():
    simulation = new_simulation(UNORDERED_TEST_CASE, MONTH)
    members = simulation.household.members
    salaries = members('salary', MONTH)
    # TODO
