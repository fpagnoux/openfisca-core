# -*- coding: utf-8 -*-

from openfisca_core.tools import assert_near
from openfisca_core.tests import dummy_country
from dummy_country import Familles

tax_benefit_system = dummy_country.DummyTaxBenefitSystem()

TEST_CASE = {
    'individus': [{'id': 'ind0'}, {'id': 'ind1'}, {'id': 'ind2'}, {'id': 'ind3'}, {'id': 'ind4'}, {'id': 'ind5'}],
    'familles': [
        {'enfants': ['ind2', 'ind3'], 'parents': ['ind0', 'ind1']},
        {'enfants': ['ind5'], 'parents': ['ind4']}
        ],
    }

simulation = tax_benefit_system.new_scenario().init_from_test_case(
    period = 2013,
    test_case = TEST_CASE
    ).new_simulation()


def test_role_index_and_positions():

    assert_near(simulation.get_role_in_entity(Familles), [0, 0, 1, 1, 0, 1])
    assert_near(simulation.get_entity_id(Familles), [0, 0, 0, 0, 1, 1])
    assert_near(simulation.get_position_in_entity(Familles), [0, 1, 2, 3, 0, 1])
