import numpy as np
import functools


def ndarrayconvert(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        new_args = []
        new_kwargs = {}

        for arg in args:
            arg = np.array(arg)
            new_args.append(arg)

        for k, arg in kwargs.items():
            arg = np.array(arg)
            new_kwargs[k] = arg

        return func(self, *new_args, **new_kwargs)

    wrapper.orig_func = func
    return wrapper
