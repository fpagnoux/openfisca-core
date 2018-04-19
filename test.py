# -*- coding: utf-8 -*-

import numpy as np


salaire = np.asarray([ 2600.,   200.,   700.,   300.,  2800.,  2900.,   900.,  2800.,
         500.,   400.,  2700.,   400.])

class GroupEntityArray(object):
  def __init__(self):
    self.members_entity_id = np.asarray([0,0,0,1,1, 2 ,2 ,2, 3, 4, 4 ,5])
    self.positions = np.asarray([0,1,2, 0,1,0,1,2,0,0,1,0])
    self.count = 2
    self.nb_persons = [3, 2]
    self._max_nb_persons = 3
    self.count = 6
    self.existence_matrix = self.get_existence_matrix()

  def get_existence_matrix(self):
    result = self._get_empty_members_matrix(False, np.bool)
    result[self.positions, self.members_entity_id] = True
    return result

  def members(self, array):
    result = self._get_empty_members_matrix(0, array.dtype)
    result[self.positions, self.members_entity_id] = array
    return PartialMatrix(result, self.existence_matrix)


  def sum(self, matrix):
    return np.where(self.existence_matrix, matrix, 0).sum(0)

  def max(self, matrix):
    return np.where(self.existence_matrix, matrix, - np.inf).max(0)

  def min(self, matrix):
    return np.where(self.existence_matrix, matrix, + np.inf).min(0)

  def all(self, matrix):
    return np.where(self.existence_matrix, matrix, True).all(0)

  def any(self, matrix):
    return np.where(self.existence_matrix, matrix, False).any(0)

  def _get_empty_members_matrix(self, default_value, dtype):
    return np.full((self._max_nb_persons, self.count), default_value, dtype)


class PartialMatrix(np.ndarray):
    def __new__(cls, matrix, existence_matrix):
        obj = np.asarray(matrix).view(cls)
        obj.existence_matrix = existence_matrix
        return obj

    # See previous comment
    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.existence_matrix = getattr(obj, 'existence_matrix', None)

entity = GroupEntityArray()
matrix = entity.members(salaire)


import ipdb; ipdb.set_trace()
