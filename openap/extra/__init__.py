import functools

import numpy as np


def ndarrayconvert(func=None, column=False):
    assert func is None or callable(func)

    def _decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            new_args = []
            new_kwargs = {}

            for arg in args:
                if not isinstance(arg, str):
                    if np.ndim(arg) == 0:
                        arg = np.array([arg])
                    else:
                        arg = np.array(arg)

                    if column:
                        arg = arg.reshape(-1, 1)
                new_args.append(arg)

            for k, arg in kwargs.items():
                if not isinstance(arg, str):
                    if np.ndim(arg) == 0:
                        arg = np.array([arg])
                    else:
                        arg = np.array(arg)

                    if column:
                        arg = arg.reshape(-1, 1)
                new_kwargs[k] = arg

            result = func(self, *new_args, **new_kwargs)

            def scalar_convert(value):
                if isinstance(value, np.ndarray):
                    if value.ndim == 0:
                        return value.item()
                    elif value.ndim == 1 and value.shape[0] == 1:
                        return value.item()
                    elif (
                        not column
                        and value.ndim > 1
                        and (value.shape[0] == 1 or value.shape[1] == 1)
                    ):
                        return value.squeeze()
                return value

            if isinstance(result, tuple):
                return tuple(scalar_convert(r) for r in result)
            else:
                return scalar_convert(result)

        wrapper.orig_func = func
        return wrapper

    return _decorator(func) if callable(func) else _decorator
