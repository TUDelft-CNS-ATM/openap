from openap import WRAP

wrap = WRAP('A320')

for func in dir(wrap):
    if callable(getattr(wrap, func)):
        if not func.startswith('_'):
            print(getattr(wrap, func)())
