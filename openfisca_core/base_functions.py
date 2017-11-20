# -*- coding: utf-8 -*-

import numpy as np

from . import periods
from periods import YEAR

# This is the same than requested_period_default_value...
def permanent_default_value(formula, simulation, period, *extra_params):
    if formula.find_function(period) is not None:
        return formula.exec_function(simulation, period, *extra_params)
    holder = formula.holder
    array = holder.default_array()
    return array

# Il semble que cette function ne soit plus jamais appellée : si la periode de calcul d'une variable ne matche pas celle de sa période de définition, une erreur sera lancée de toute façon
def requested_period_added_value(formula, simulation, period, *extra_params):
    # This formula is used for variables that can be added to match requested period.
    holder = formula.holder
    variable = holder.variable
    period_size = period.size
    period_unit = period.unit
    if holder._array_by_period is not None and (period_size > 1 or period_unit == YEAR):
        after_instant = period.start.offset(period_size, period_unit)
        if period_size > 1:
            array = formula.zeros(dtype = variable.dtype)
            sub_period = period.start.period(period_unit)
            while sub_period.start < after_instant:
                sub_array = holder._array_by_period.get(sub_period)
                if sub_array is None:
                    array = None
                    break
                array += sub_array
                sub_period = sub_period.offset(1)
            if array is not None:
                return array
        if period_unit == YEAR:
            array = formula.zeros(dtype = variable.dtype)
            month = period.start.period(u'month')
            while month.start < after_instant:
                month_array = holder._array_by_period.get(month)
                if month_array is None:
                    array = None
                    break
                array += month_array
                month = month.offset(1)
            if array is not None:
                return array
    if formula.find_function(period) is not None:
        return formula.exec_function(simulation, period, *extra_params)
    array = holder.default_array()
    return array


def requested_period_default_value(formula, simulation, period, *extra_params):
    if formula.find_function(period) is not None:
        return formula.exec_function(simulation, period, *extra_params)
    holder = formula.holder
    array = holder.default_array()
    return array


def requested_period_last_value(formula, simulation, period, *extra_params, **kwargs):
    # This formula is used for variables that are constants between events and period size independent.
    # It returns the latest known value for the requested period.
    function = formula.find_function(period)
    if function is not None:
        return formula.exec_function(simulation, period, *extra_params)

    accept_future_value = kwargs.pop('accept_future_value', False)
    holder = formula.holder
    known_periods = holder.known_periods()
    if not known_periods:
        return holder.default_array()
    known_periods = sorted(known_periods, cmp = periods.compare_period_start, reverse = True)
    for last_period in known_periods:
        if last_period.start <= period.start:
            return holder.get_array(last_period, extra_params)
    if accept_future_value:
        next_period = known_periods[-1]
        return holder.get_array(next_period, extra_params)
    return holder.default_array()


def requested_period_last_or_next_value(formula, simulation, period, *extra_params):
    # This formula is used for variables that are constants between events and period size independent.
    # It returns the latest known value for the requested period, or the next value if there is no past value.
    return requested_period_last_value(formula, simulation, period, *extra_params, accept_future_value = True)


def missing_value(formula, simulation, period, *extra_params):
    function = formula.find_function(period)
    if function is not None:
        return formula.exec_function(simulation, period, *extra_params)
    holder = formula.holder
    variable = holder.variable
    raise ValueError(u"Missing value for variable {} at {}".format(variable.name, period))
