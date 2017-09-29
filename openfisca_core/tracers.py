# -*- coding: utf-8 -*-

class Tracer(object):

    def __init__(self):
        self.trace = {}
        self.stack = [self.trace]

    def start(self, variable_name, period):
        key = "{}<{}>".format(variable_name, period).encode('utf-8')
        current = self.stack[-1]
        if not current.get(key):  # Variable has already been computed
            current[key] = {}
        self.stack.append(current[key])

    def stop(self, variable_name, period, result):
        current = self.stack[-1]
        current['_value_'] = str(result)
        self.stack.pop()  # Get out of current node

