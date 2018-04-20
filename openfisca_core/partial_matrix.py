# -*- coding: utf-8 -*-

import numpy as np

class PartialMatrix(np.ndarray):
    def __new__(cls, matrix, existence_matrix):
        obj = np.asarray(matrix).view(cls)
        obj.existence_matrix = existence_matrix
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.existence_matrix = getattr(obj, 'existence_matrix', None)

    def max(self):
        return np.where(self.existence_matrix, self, - np.inf).max(0).view(np.ndarray)

    def min(self):
        return np.where(self.existence_matrix, self, + np.inf).min(0).view(np.ndarray)

    def sum(self):
        return np.where(self.existence_matrix, self, 0).sum(0).view(np.ndarray)

    def all(self):
        return np.where(self.existence_matrix, self, True).all(0).view(np.ndarray)

    def any(self):
        return np.where(self.existence_matrix, self, False).any(0).view(np.ndarray)

