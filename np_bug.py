import numpy as np

# I create a sublass of np.ndarray containing a custom attribute
class CustomArray(np.ndarray):
    def __new__(cls, matrix, custom_attribute):
        obj = np.asarray(matrix).view(cls)
        obj.custom_attribute = custom_attribute
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.custom_attribute = getattr(obj, 'custom_attribute', None)

x = CustomArray(np.asarray([1,2,3]), 'some_value')  # a custom array
y = np.asarray([4,5,6])  # a regular array

# Sublass is preserved by most operations
assert type(x + y) == CustomArray
assert type(x * y) == CustomArray
assert type(np.maximum(x, y)) == CustomArray
assert type(np.logical_not((x > 1) * (y <= 5))) == CustomArray

# But not select and where

where_result = np.where(x <= 1, x + 1, x)

select_result = np.select(
  [[x <= 1], [x <= 2]],
  [[x + 1], [x + 2]],
  x
  )

assert type(where_result) == CustomArray
assert type(select_result) == CustomArray
