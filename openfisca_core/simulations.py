# -*- coding: utf-8 -*-


import collections
import warnings

import numpy as np

from . import periods, holders
from .tools import empty_clone, stringify_array


class Simulation(object):
    compact_legislation_by_instant_cache = None
    debug = False
    debug_all = False  # When False, log only formula calls with non-default parameters.
    period = None
    reference_compact_legislation_by_instant_cache = None
    stack_trace = None
    steps_count = 1
    tax_benefit_system = None
    trace = False
    traceback = None

    def __init__(self, debug = False, debug_all = False, period = None, tax_benefit_system = None,
    trace = False, opt_out_cache = False):
        assert isinstance(period, periods.Period)
        self.period = period
        self.holder_by_name = {}

        # To keep track of the values (formulas and periods) being calculated to detect circular definitions.
        # See use in formulas.py.
        # The data structure of requested_periods_by_variable_name is: {variable_name: [period1, period2]}
        self.requested_periods_by_variable_name = {}
        self.max_nb_cycles = None

        if debug:
            self.debug = True
        if debug_all:
            assert debug
            self.debug_all = True
        assert tax_benefit_system is not None
        self.tax_benefit_system = tax_benefit_system
        if trace:
            self.trace = True
        self.opt_out_cache = opt_out_cache
        if debug or trace:
            self.stack_trace = collections.deque()
            self.traceback = collections.OrderedDict()

        # Note: Since simulations are short-lived and must be fast, don't use weakrefs for cache.
        self.compact_legislation_by_instant_cache = {}
        self.reference_compact_legislation_by_instant_cache = {}

        self.entity_count = dict(
            (entity.key, {"step_size": 0, "count": 0})
            for entity in self.tax_benefit_system.entities
            )

    def calculate(self, column_name, period = None, **parameters):
        if period is None:
            period = self.period
        return self.compute(column_name, period = period, **parameters).array

    def calculate_add(self, column_name, period = None, **parameters):
        if period is None:
            period = self.period
        return self.compute_add(column_name, period = period, **parameters).array

    def calculate_add_divide(self, column_name, period = None, **parameters):
        if period is None:
            period = self.period
        return self.compute_add_divide(column_name, period = period, **parameters).array

    def calculate_divide(self, column_name, period = None, **parameters):
        if period is None:
            period = self.period
        return self.compute_divide(column_name, period = period, **parameters).array

    def calculate_output(self, column_name, period = None):
        """Calculate the value using calculate_output hooks in formula classes."""
        if period is None:
            period = self.period
        elif not isinstance(period, periods.Period):
            period = periods.period(period)
        holder = self.get_or_new_holder(column_name)
        return holder.calculate_output(period)

    def clone(self, debug = False, debug_all = False, trace = False):
        """Copy the simulation just enough to be able to run the copy without modifying the original simulation."""
        new = empty_clone(self)
        new_dict = new.__dict__

        for key, value in self.__dict__.iteritems():
            if key not in ('debug', 'debug_all', 'trace'):
                new_dict[key] = value

        if debug:
            new_dict['debug'] = True
        if debug_all:
            new_dict['debug_all'] = True
        if trace:
            new_dict['trace'] = True
        if debug or trace:
            new_dict['stack_trace'] = collections.deque()
            new_dict['traceback'] = collections.OrderedDict()

        new_dict['holder_by_name'] = {
            name: holder.clone()
            for name, holder in self.holder_by_name.iteritems()
            }
        return new

    def compute(self, column_name, period = None, **parameters):
        if period is None:
            period = self.period
        elif not isinstance(period, periods.Period):
            period = periods.period(period)
        print_trace = parameters.pop('print_trace', False)
        if print_trace:
            print_trace_kwargs = {}
            max_depth = parameters.pop('max_depth', None)
            if max_depth is not None:
                print_trace_kwargs['max_depth'] = max_depth
            show_default_values = parameters.pop('show_default_values', None)
            if show_default_values is not None:
                print_trace_kwargs['show_default_values'] = show_default_values
        if (self.debug or self.trace) and self.stack_trace:
            variable_infos = (column_name, period)
            calling_frame = self.stack_trace[-1]
            caller_input_variables_infos = calling_frame['input_variables_infos']
            if variable_infos not in caller_input_variables_infos:
                caller_input_variables_infos.append(variable_infos)
        holder = self.get_or_new_holder(column_name)
        result = holder.compute(period = period, **parameters)
        if print_trace:
            self.print_trace(variable_name=column_name, period=period, **print_trace_kwargs)
        return result

    def compute_add(self, column_name, period = None, **parameters):
        if period is None:
            period = self.period
        elif not isinstance(period, periods.Period):
            period = periods.period(period)
        if (self.debug or self.trace) and self.stack_trace:
            variable_infos = (column_name, period)
            calling_frame = self.stack_trace[-1]
            caller_input_variables_infos = calling_frame['input_variables_infos']
            if variable_infos not in caller_input_variables_infos:
                caller_input_variables_infos.append(variable_infos)
        holder = self.get_or_new_holder(column_name)
        return holder.compute_add(period = period, **parameters)

    def compute_add_divide(self, column_name, period = None, **parameters):
        if period is None:
            period = self.period
        elif not isinstance(period, periods.Period):
            period = periods.period(period)
        if (self.debug or self.trace) and self.stack_trace:
            variable_infos = (column_name, period)
            calling_frame = self.stack_trace[-1]
            caller_input_variables_infos = calling_frame['input_variables_infos']
            if variable_infos not in caller_input_variables_infos:
                caller_input_variables_infos.append(variable_infos)
        holder = self.get_or_new_holder(column_name)
        return holder.compute_add_divide(period = period, **parameters)

    def compute_divide(self, column_name, period = None, **parameters):
        if period is None:
            period = self.period
        elif not isinstance(period, periods.Period):
            period = periods.period(period)
        if (self.debug or self.trace) and self.stack_trace:
            variable_infos = (column_name, period)
            calling_frame = self.stack_trace[-1]
            caller_input_variables_infos = calling_frame['input_variables_infos']
            if variable_infos not in caller_input_variables_infos:
                caller_input_variables_infos.append(variable_infos)
        holder = self.get_or_new_holder(column_name)
        return holder.compute_divide(period = period, **parameters)

    def get_array(self, column_name, period = None):
        if period is None:
            period = self.period
        elif not isinstance(period, periods.Period):
            period = periods.period(period)
        if (self.debug or self.trace) and self.stack_trace:
            variable_infos = (column_name, period)
            calling_frame = self.stack_trace[-1]
            caller_input_variables_infos = calling_frame['input_variables_infos']
            if variable_infos not in caller_input_variables_infos:
                caller_input_variables_infos.append(variable_infos)
        return self.get_or_new_holder(column_name).get_array(period)

    def get_compact_legislation(self, instant):
        compact_legislation = self.compact_legislation_by_instant_cache.get(instant)
        if compact_legislation is None:
            compact_legislation = self.tax_benefit_system.get_compact_legislation(
                instant = instant,
                traced_simulation = self if self.trace else None,
                )
            self.compact_legislation_by_instant_cache[instant] = compact_legislation
        return compact_legislation

    def get_holder(self, column_name, default = UnboundLocalError):
        if default is UnboundLocalError:
            return self.holder_by_name[column_name]
        return self.holder_by_name.get(column_name, default)

    def get_or_new_holder(self, column_name):
        holder = self.holder_by_name.get(column_name)
        if holder is None:
            column = self.tax_benefit_system.get_column(column_name, check_existence = True)
            self.holder_by_name[column_name] = holder = holders.Holder(
                self,
                column = column,
                )
            if column.formula_class is not None:
                holder.formula = column.formula_class(holder = holder)
        return holder

    def get_reference_compact_legislation(self, instant):
        reference_compact_legislation = self.reference_compact_legislation_by_instant_cache.get(instant)
        if reference_compact_legislation is None:
            reference_compact_legislation = self.tax_benefit_system.get_reference_compact_legislation(
                instant = instant,
                traced_simulation = self if self.trace else None,
                )
            self.reference_compact_legislation_by_instant_cache[instant] = reference_compact_legislation
        return reference_compact_legislation

    def graph(self, column_name, edges, get_input_variables_and_parameters, nodes, visited):
        self.get_or_new_holder(column_name).graph(edges, get_input_variables_and_parameters, nodes, visited)

    def legislation_at(self, instant, reference = False):
        assert isinstance(instant, periods.Instant), "Expected an instant. Got: {}".format(instant)
        if reference:
            return self.get_reference_compact_legislation(instant)
        return self.get_compact_legislation(instant)

    def find_traceback_step(self, variable_name, period):
        assert isinstance(period, periods.Period), period
        column = self.tax_benefit_system.get_column(variable_name, check_existence=True)
        step = self.traceback.get((variable_name, period))
        if step is None and column.is_period_size_independent:
            period = None
        step = self.traceback.get((variable_name, period))
        return step

    def print_trace(self, variable_name, period, max_depth=3, show_default_values=True):
        """
        Print the dependencies of all the variables computed since the creation of the simulation.

        The `max_depth` parameter tells how much levels of the printed tree to show. Use -1 to disable limit.

        The simulation must have been initialized with `trace=True` argument.
        """
        def traverse(current_variable_name, current_period, depth):
            step = self.find_traceback_step(current_variable_name, current_period)
            assert step is not None
            holder = self.get_holder(current_variable_name)
            has_default_value = np.all(holder.get_array(current_period) == holder.column.default)
            if depth == 0 or (show_default_values or not has_default_value):
                indent = u'|     ' * (depth - 1) + u'|---> ' \
                    if depth > 0 \
                    else ''
                print(indent + self.stringify_variable_for_period_with_array(current_variable_name, current_period))
            input_variables_infos = step.get('input_variables_infos')
            if (max_depth == -1 or depth < max_depth) and input_variables_infos is not None:
                    for index, (child_variable_name, child_period) in enumerate(input_variables_infos):
                        traverse(child_variable_name, child_period, depth + 1)
        if not isinstance(max_depth, int) or max_depth < -1:
            raise ValueError(u'`max_depth` argument must be >= -1')
        if not self.trace:
            raise ValueError(u'This simulation has not been initialized with `trace=True` so the computation '
                'did not collect any trace information.')
        assert self.traceback is not None
        if not isinstance(period, periods.Period):
            period = periods.period(period)
        step = self.find_traceback_step(variable_name, period)
        if step is None:
            raise ValueError(u'The given `variable_name` "{0}" was not calculated for the given `period` "{1}". '
                u'It is therefore not possible to display the trace. '
                u'You should do `simulation.calculate({0!r}, {1}, print_trace=True)`.'.format(
                    variable_name, period))
        traverse(variable_name, period, depth=0)

    def stringify_variable_for_period_with_array(self, variable_name, period):
        holder = self.get_holder(variable_name)
        return u'{}@{}<{}>{}'.format(
            variable_name,
            holder.entity.key,
            str(period),
            stringify_array(holder.get_array(period)),
            )

    def stringify_input_variables_infos(self, input_variables_infos):
        return u', '.join(
            self.stringify_variable_for_period_with_array(
                variable_name=input_variable_name,
                period=input_variable_period,
                )
            for input_variable_name, input_variable_period in input_variables_infos
            )

    # Fixme: to rewrite
    def to_input_variables_json(self):
        return None

    def get_variable_entity(self, variable_name):
        column = self.tax_benefit_system.get_column(variable_name, check_existence = True)
        return column.entity_class

    def set_entity_count(self, entity, count):
        self.entity_count[entity.key]['count'] = count

    def set_entity_step_size(self, entity, step_size):
        self.entity_count[entity.key]['step_size'] = step_size

    def get_entity_step_size(self, entity):
        return self.entity_count[entity.key]['step_size']

    def get_entity_count(self, entity):
        return self.entity_count[entity.key]['count']

    def get_entity_index_array(self, entity):
        tbs = self.tax_benefit_system
        index_column_name = tbs.get_entity_index_column_name(entity)
        return self.holder_by_name[index_column_name].array

    def get_role_in_entity(self, entity):
        tbs = self.tax_benefit_system
        role_column_name = tbs.get_entity_role_column_name(entity)
        return self.holder_by_name[role_column_name].array

    def get_entity_position_array(self, entity):
        tbs = self.tax_benefit_system
        position_column_name = tbs.get_entity_position_column_name(entity)
        return self.holder_by_name[position_column_name].array

    def transpose_to_entity(self, array, target_entity, origin_entity):
        input_projected = self.project_on_first_person(array, entity = origin_entity)
        return self.sum_in_entity(input_projected, entity = target_entity)

    #  Aggregation persons -> entity

    def sum_in_entity(self, array, entity, role = None):

        entity_index_array = self.get_entity_index_array(entity)
        result = self.empty_array(entity)
        if role is not None:
            entity_role_array = self.get_role_in_entity(entity)
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
        position_in_entity = self.get_entity_position_array(entity)
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

    # Projection person -> entity

    def value_from_person(self, array, entity, role, default = 0):
        # TODO: Make sure there is unique
        result = self.filled_array(entity, default)
        role_filter = (self.get_role_in_entity(entity) == role)
        entity_filter = self.any_in_entity(role_filter, entity)

        result[entity_filter] = array[role_filter]

        return result

    # Projection entity -> person(s)

    def project_on_persons(self, array, entity):  # should take a role
        entity_index_array = self.get_entity_index_array(entity)
        return array[entity_index_array]

    def project_on_first_person(self, array, entity):
        entity_position_array = self.get_entity_position_array(entity)
        entity_index_array = self.get_entity_index_array(entity)
        boolean_filter = (entity_position_array == 0)
        return array[entity_index_array] * boolean_filter

    def empty_array(self, entity):
        return np.zeros(self.get_entity_count(entity))

    def filled_array(self, entity, value):
        with warnings.catch_warnings():  # Avoid a non-relevant warning
            warnings.simplefilter("ignore")
            return np.full(self.get_entity_count(entity), value)
