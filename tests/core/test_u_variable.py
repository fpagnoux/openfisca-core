import datetime

import pytest

from openfisca_core.variables import Variable
from openfisca_core import periods
from openfisca_core.periods import period as make_period
from openfisca_core.errors import PeriodMismatchError

class VariableStub(Variable):

    def __init__(self):
        pass

def test_is_inactive():
    variable = VariableStub()
    variable.end = datetime.date(2018, 5, 31)

    assert variable.is_inactive(make_period('2018-06'))
    assert not variable.is_inactive(make_period('2018-05'))



@pytest.mark.parametrize("definition_period, period", [
    (periods.MONTH, '2019-01'),
    (periods.YEAR, '2019'),
    (periods.ETERNITY, '2019-01'),
    (periods.ETERNITY, '2019'),
    (periods.ETERNITY, periods.ETERNITY),
    ])
def test_check_input_period_ok(definition_period, period):
    variable = VariableStub()
    variable.definition_period = definition_period
    variable.check_input_period(make_period(period))

@pytest.mark.parametrize("definition_period, period", [
    (periods.MONTH, periods.ETERNITY),
    (periods.MONTH, 2018),
    (periods.MONTH, "month:2018-01:3"),
    (periods.YEAR, periods.ETERNITY),
    (periods.YEAR, "2018-01"),
    (periods.YEAR, "year:2018:2"),
    ])
def test_period_mismatch(definition_period, period):
    variable = VariableStub()
    variable.definition_period = definition_period
    variable.name = 'salary'

    with pytest.raises(PeriodMismatchError):
        variable.check_input_period(make_period(period))

