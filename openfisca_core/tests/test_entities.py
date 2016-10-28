# -*- coding: utf-8 -*-

from copy import deepcopy

from openfisca_core.tools import assert_near
from dummy_country import Familles, Individus
from test_countries import tax_benefit_system

TEST_CASE = {
    'individus': [{'id': 'ind0'}, {'id': 'ind1'}, {'id': 'ind2'}, {'id': 'ind3'}, {'id': 'ind4'}, {'id': 'ind5'}],
    'familles': [
        {'enfants': ['ind2', 'ind3'], 'parents': ['ind0', 'ind1']},
        {'enfants': ['ind5'], 'parents': ['ind4']}
        ],
    }

TEST_CASE_AGES = deepcopy(TEST_CASE)
AGES = [40, 37, 7, 9, 54, 20]
for (individu, age) in zip(TEST_CASE_AGES['individus'], AGES):
        individu['age'] = age

ROLES_DANS_FAMILLE = Familles.get_role_enum()
PARENT = ROLES_DANS_FAMILLE['parents']
ENFANT = ROLES_DANS_FAMILLE['enfants']


def new_simulation(test_case):
    return tax_benefit_system.new_scenario().init_from_test_case(
        period = 2013,
        test_case = test_case
        ).new_simulation()


def test_role_index_and_positions():
    simulation = new_simulation(TEST_CASE)
    assert_near(simulation.get_entity(Familles).members_role, [PARENT, PARENT, ENFANT, ENFANT, PARENT, ENFANT])
    assert_near(simulation.get_entity(Familles).members_legacy_role, [0, 1, 2, 3, 0, 2])
    assert_near(simulation.get_entity(Familles).members_entity_id, [0, 0, 0, 0, 1, 1])
    assert_near(simulation.get_entity(Familles).members_position, [0, 1, 2, 3, 0, 1])


def test_project():
    test_case = deepcopy(TEST_CASE)
    test_case['familles'][0]['af'] = 20000

    simulation = new_simulation(test_case)
    familles = simulation.get_entity(Familles)

    af = familles['af'](2013)
    af_projete = familles.project(af)

    assert_near(af_projete, [20000, 20000, 20000, 20000, 0, 0])

    af_projete_parents = familles.project(af, role = PARENT)
    assert_near(af_projete_parents, [20000, 20000, 0, 0, 0, 0])


def test_project_on_first_person():
    test_case = deepcopy(TEST_CASE)
    test_case['familles'][0]['af'] = 20000
    test_case['familles'][1]['af'] = 5000

    simulation = new_simulation(test_case)
    familles = simulation.get_entity(Familles)

    af = familles['af']()
    af_projete = familles.project_on_first_person(af)

    assert_near(af_projete, [20000, 0, 0, 0, 5000, 0])


def test_share_between_members():
    test_case = deepcopy(TEST_CASE)
    test_case['familles'][0]['af'] = 20000
    test_case['familles'][1]['af'] = 5000

    simulation = new_simulation(test_case)
    familles = simulation.get_entity(Familles)

    af = familles['af']()

    af_shared = familles.share_between_members(af, role = PARENT)

    assert_near(af_shared, [10000, 10000, 0, 0, 5000, 0])


def test_sum():
    test_case = deepcopy(TEST_CASE)
    test_case['individus'][0]['salaire_net'] = 1000
    test_case['individus'][1]['salaire_net'] = 1500
    test_case['individus'][4]['salaire_net'] = 3000
    test_case['individus'][5]['salaire_net'] = 500

    simulation = new_simulation(test_case)
    familles = simulation.get_entity(Familles)

    salaire_net = familles.members['salaire_net']()
    salaire_total_par_famille = familles.sum(salaire_net)

    assert_near(salaire_total_par_famille, [2500, 3500])

    salaire_total_parents_par_famille = familles.sum(salaire_net, role = PARENT)

    assert_near(salaire_total_parents_par_famille, [2500, 3000])


def test_any():
    test_case = deepcopy(TEST_CASE_AGES)
    simulation = new_simulation(test_case)
    familles = simulation.get_entity(Familles)

    age = familles.members['age']()
    condition_age = (age <= 18)
    has_famille_member_with_age_inf_18 = familles.any(condition_age)
    assert_near(has_famille_member_with_age_inf_18, [True, False])

    condition_age_2 = (age > 18)
    has_famille_enfant_with_age_sup_18 = familles.any(condition_age_2, role = ENFANT)
    assert_near(has_famille_enfant_with_age_sup_18, [False, True])


def test_all():
    test_case = deepcopy(TEST_CASE_AGES)
    simulation = new_simulation(test_case)
    familles = simulation.get_entity(Familles)

    age = familles.members['age']()

    condition_age = (age >= 18)
    all_persons_age_sup_18 = familles.all(condition_age)
    assert_near(all_persons_age_sup_18, [False, True])

    all_parents_age_sup_18 = familles.all(condition_age, role = PARENT)
    assert_near(all_parents_age_sup_18, [True, True])


def test_max():
    test_case = deepcopy(TEST_CASE_AGES)
    simulation = new_simulation(test_case)
    familles = simulation.get_entity(Familles)

    age = familles.members['age']()

    age_max = familles.max(age)
    assert_near(age_max, [40, 54])

    age_max_enfants = familles.max(age, role = ENFANT)
    assert_near(age_max_enfants, [9, 20])


def test_min():
    test_case = deepcopy(TEST_CASE_AGES)
    simulation = new_simulation(test_case)
    familles = simulation.get_entity(Familles)

    age = familles.members['age']()

    age_min = familles.min(age)
    assert_near(age_min, [7, 20])

    age_min_parents = familles.min(age, role = PARENT)
    assert_near(age_min_parents, [37, 54])


def test_swap():
    test_case = deepcopy(TEST_CASE)
    test_case['individus'][0]['salaire_net'] = 1000
    test_case['individus'][1]['salaire_net'] = 1500
    test_case['individus'][4]['salaire_net'] = 3000
    test_case['individus'][5]['salaire_net'] = 500

    simulation = new_simulation(test_case)
    individus = simulation.get_entity(Individus)

    salaire_net = individus['salaire_net']()

    salaire_conjoint = individus.value_from_partner(salaire_net, individus.famille, PARENT)

    assert_near(salaire_conjoint, [1500, 1000, 0, 0, 0, 0])
