# -*- coding: utf-8 -*-

import numpy as np
from enum import Enum as BaseEnum


class EnumArray(np.ndarray):
    """
        Numpy array subclass representing an array of enum items
    """

    def __new__(cls, input_array, enum = None):
        obj = np.asarray(input_array).view(cls)
        obj.enum = enum
        return obj

    def __array_finalize__(self, obj):
        if obj is None: return
        self.enum = getattr(obj, 'enum', None)

    def __array_wrap__(self, out_arr, context = None):
        return super(MySubClass, self).__array_wrap__(self, out_arr, context)

    def __eq__(self, other):
        if other.__class__ is self.enum:
            return self.view(np.ndarray) == other.index
        return self.view(np.ndarray) == other

    def __ne__(self, other):
        return np.logical_not(self == other)

    def __add__(self, other):
        raise TypeError("Cannot sum EnumArrays")

    def __mul__(self, other):
        raise TypeError("Cannot multiply EnumArrays")

    def decode(self):
        return np.select([self == item.index for item in self.enum], [item for item in self.enum])

    def __repr__(self):
        from nose.tools import set_trace; set_trace(); import ipdb; ipdb.set_trace()
        try:
            return '{}({})'.format(self.__class__.__name__, str(self.decode()))
        except:
            return np.ndarray.__repr__(self)

class Enum(BaseEnum):
    def __init__(self, name):
        self.index = len(self._member_names_)
