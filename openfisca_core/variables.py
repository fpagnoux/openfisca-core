import inspect
import textwrap

from openfisca_core.formulas import SimpleFormula, DatedFormula, new_filled_column


class AbstractVariable(object):
    formula_class = None

    def __init__(self, name, attributes, variable_class):
        self.name = name
        self.attributes = {attr_name.strip('_'): attr_value for (attr_name, attr_value) in attributes.iteritems()}
        self.variable_class = variable_class

    def introspect(self):
        comments = inspect.getcomments(self.variable_class)

        # Handle dynamically generated variable classes or Jupyter Notebooks, which have no source.
        try:
            source_file_path = inspect.getsourcefile(self.variable_class)
        except TypeError:
            source_file_path = None
        try:
            source_lines, line_number = inspect.getsourcelines(self.variable_class)
            source_code = textwrap.dedent(''.join(source_lines))
        except (IOError, TypeError):
            source_code, line_number = None, None

        return (comments, source_file_path, source_code, line_number)

    def to_column(self, tax_benefit_system):
        formula_class = self.__class__.formula_class
        entity = self.attributes.pop('entity', None)

        # For reform variable that replaces the existing reference one
        reference = self.attributes.pop('reference', None)
        if reference:
            if not entity:
                entity = reference.entity

        (comments, source_file_path, source_code, line_number) = self.introspect()

        if entity is None:
            raise Exception('Variable {} must have an entity'.format(self.name))

        return new_filled_column(
            name = self.name,
            entity = entity,
            formula_class = formula_class,
            reference_column = reference,
            comments = comments,
            line_number = line_number,
            source_code = source_code,
            source_file_path = source_file_path,
            base_function = self.attributes.pop('base_function', UnboundLocalError),
            calculate_output = self.attributes.pop('calculate_output', UnboundLocalError),
            cerfa_field = self.attributes.pop('cerfa_field', UnboundLocalError),
            column = self.attributes.pop('column', UnboundLocalError),
            doc = self.attributes.pop('doc', UnboundLocalError),
            is_permanent = self.attributes.pop('is_permanent', UnboundLocalError),
            label = self.attributes.pop('label', UnboundLocalError),
            law_reference = self.attributes.pop('law_reference', UnboundLocalError),
            module = self.attributes.pop('module', UnboundLocalError),
            set_input = self.attributes.pop('set_input', UnboundLocalError),
            start_date = self.attributes.pop('start_date', UnboundLocalError),
            stop_date = self.attributes.pop('stop_date', UnboundLocalError),
            url = self.attributes.pop('url', UnboundLocalError),
            **self.attributes
            )


class Variable(AbstractVariable):
    formula_class = SimpleFormula


class DatedVariable(AbstractVariable):
    formula_class = DatedFormula
