# -*- coding: utf-8 -*-

import numpy as np

from indexed_enums import EnumArray

class PartialMatrix(np.ndarray):
    def __new__(cls, matrix, existence_matrix):
        obj = matrix.view(cls)
        obj.existence_matrix = existence_matrix
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.existence_matrix = getattr(obj, 'existence_matrix', None)

    def max(self):
        return np.where(self.existence_matrix, self, - np.inf).max(0).view(np.ndarray)

    def min(self):
        return np.where(self.existence_matrix, self, + np.inf).min(0)

    def sum(self):
        return (self.existence_matrix * self).view(np.ndarray).sum(0).view(np.ndarray)

    def all(self):
        return np.where(self.existence_matrix, self, True).all(0).view(np.ndarray)

    def any(self):
        return np.where(self.existence_matrix, self, False).any(0).view(np.ndarray)


class PartialEnumMatrix(PartialMatrix, EnumArray):
    def __new__(cls, matrix, possible_values, existence_matrix):
        obj = matrix.view(cls)
        obj.existence_matrix = existence_matrix
        obj.possible_values = possible_values
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.existence_matrix = getattr(obj, 'existence_matrix', None)
        self.possible_values = getattr(obj, 'possible_values', None)

    def __eq__(self, other):
        result = EnumArray.__eq__(self, other)
        return PartialMatrix(result, self.existence_matrix)
