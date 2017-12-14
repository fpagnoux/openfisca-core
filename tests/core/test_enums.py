# # -*- coding: utf-8 -*-


# from openfisca_core.indexedenums import EnumArray, Enum
# from openfisca_core.model_api import *
# import numpy as np
# class TypesActivite(Enum):
#     actif = u'Actif occupé'
#     chomeur = u'Chômeur'
#     etudiant = u'Étudiant, élève'
#     retraite = u'Retraité'
#     inactif = u'Autre, inactif'


# def encode_enum(array, enum):
#     if array.dtype.kind in {'U', 'S'}:  # String array
#         array = np.select([array == item.name for item in enum], [item.index for item in enum]).astype(self.variable.dtype)
#     elif array.dtype.kind == 'O':  # Enum items arrays
#         array = np.select([array == item for item in enum], [item.index for item in enum]).astype(self.variable.dtype)
#     array = EnumArray(array, enum)

#     return array


# array = np.asarray(range(4))
# encoded_array = encode_enum(array, TypesActivite)

# x = where(True, encoded_array, encoded_array)
# from nose.tools import set_trace; set_trace(); import ipdb; ipdb.set_trace()


# # class MySubClass(np.ndarray):

# #     def __new__(cls, input_array, info=None):
# #         obj = np.asarray(input_array).view(cls)
# #         obj.info = info
# #         return obj

# #     def __array_finalize__(self, obj):
# #         print('In __array_finalize__:')
# #         print('   self is %s' % repr(self))
# #         print('   obj is %s' % repr(obj))
# #         if obj is None: return
# #         self.info = getattr(obj, 'info', None)

# #     def __array_wrap__(self, out_arr, context=None):
# #         print('In __array_wrap__:')
# #         print('   self is %s' % repr(self))
# #         print('   arr is %s' % repr(out_arr))
# #         # then just call the parent
# #         return super(MySubClass, self).__array_wrap__(self, out_arr, context)

# # obj = MySubClass(np.arange(5), info='spam')
# # # In __array_finalize__:
# # #    self is MySubClass([0, 1, 2, 3, 4])
# # #    obj is array([0, 1, 2, 3, 4])
# # arr2 = np.arange(5)+1
# # ret = np.select([True] * 5, obj)
# # assert(isinstance(ret, MySubClass))
# # # In __array_wrap__:
# # #    self is MySubClass([0, 1, 2, 3, 4])
# # #    arr is array([1, 3, 5, 7, 9])
# # # In __array_finalize__:
# # #    self is MySubClass([1, 3, 5, 7, 9])
# # #    obj is MySubClass([0, 1, 2, 3, 4])
# # print(ret)
# # # MySubClass([1, 3, 5, 7, 9])
# # print(ret.info)
# # # 'spam'
