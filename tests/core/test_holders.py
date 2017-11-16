# -*- coding: utf-8 -*-

import numpy as np
from nose.tools import assert_equal

from openfisca_core.simulations import Simulation
from openfisca_core.periods import period
from openfisca_core.tools import assert_near
from openfisca_country_template.situation_examples import single
from test_countries import tax_benefit_system

def get_simulation():
    return Simulation(tax_benefit_system = tax_benefit_system, simulation_json = single)

def test_delete_arrays():
    simulation = get_simulation()
    salary_holder = simulation.person.get_holder('salary')
    salary_holder.set_input( period(2017), np.asarray([30000]))
    salary_holder.set_input( period(2018), np.asarray([60000]))
    assert_equal(simulation.person('salary', '2017-01'), 2500)
    assert_equal(simulation.person('salary', '2018-01'), 5000)
    salary_holder.delete_arrays(period = 2018)
    assert_equal(simulation.person('salary', '2017-01'), 2500)
    assert_equal(simulation.person('salary', '2018-01'), 0)

def test_cache_disk():
    simulation = get_simulation()
    month = period('2017-01')
    holder = simulation.person.get_holder('salary')
    data = np.asarray([2000, 3000, 0, 500])
    holder.put_in_disk_cache(data, month)
    stored_data = holder.get_from_disk_cache(month).array
    assert_near(data, stored_data)
