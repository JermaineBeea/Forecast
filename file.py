def func (a = 1, b = 2):
    print(a, b)

args = {'a': 3, 'b': 4}

from functools import partial

partial(func, **args)()
