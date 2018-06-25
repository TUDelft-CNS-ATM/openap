import math

class Interval:

    @classmethod
    def cast(cls, x):
        if isinstance(x, cls):
            return x
        try:
            y = float(x)
        except:
            raise RuntimeError("Invalid scalar: " + repr(x))
        return Interval(y, y)

    def __repr__(self):
        return "Interval(%f, %f)" % (self.lo, self.hi)

    def __init__(self, lo, hi):
        self.lo = float(min(lo, hi))
        self.hi = float(max(lo, hi))

    def __pos__(self):
        return self

    def __neg__(self):
        return Interval(-self.hi, -self.lo)

    def __add__(self, other):
        other = self.cast(other)
        return Interval(self.lo+other.lo, self.hi+other.hi)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return (-self) + other

    def __mul__(self, other):
        other = self.cast(other)
        bounds = [self.lo*other.lo, self.lo*other.hi,
                  self.hi*other.lo, self.hi*other.hi]
        return Interval(min(bounds), max(bounds))

    def __rmul__(self, other):
        return self * other

    def __div__(self, other):
        other = self.cast(other)
        if other.lo > 0 or other.hi < 0:
            other_inverse = Interval(1/other.lo, 1/other.hi)
            return self * other_inverse
        else:
            raise RuntimeError("Interval division on ZERO occured.")

    def __rdiv__(self, other):
        if self.lo > 0 or self.hi < 0:
            other = self.cast(other)
            self_inverse = Interval(1/self.lo, 1/self.hi)
            return other * self_inverse
        else:
            raise RuntimeError("Interval division on ZERO occured.")

    def sqrt(self):
        if self.hi < 0:
            raise RuntimeError("Interval must be partically positive")
        else:
            hi = self.hi
        if self.lo < 0:
            lo = 0
        else:
            lo = self.lo
        return Interval(math.sqrt(lo), math.sqrt(hi))

    def bounds(self):
        """ cast interval to tuple"""
        return (self.lo, self.hi)


def test_interval_funtions():
    a = Interval(2, 6)
    b = Interval(-5, 3)
    c = 10

    print("a =", a)
    print("b =", b)
    print("c =", c)

    ab_add = a + b
    ac_add = a + c
    ca_add = c + a

    print("a + b =", ab_add)
    print("a + c =", ac_add)
    print("c + a =", ca_add)

    ab_sub = a - b
    ac_sub = a - c
    ca_sub = c - a

    print("a - b =", ab_sub)
    print("a - c =", ac_sub)
    print("c - a =", ca_sub)

    ab_mul = a * b
    ac_mul = a * c
    ca_mul = c * a

    print("a x b =", ab_mul)
    print("a x c =", ac_mul)
    print("c x a =", ca_mul)

    try:
        ab_div = a / b
    except:
        ab_div = 'inf'

    try:
        ba_div = b / a
    except:
        ba_div = 'inf'

    try:
        ac_div = a / c
    except:
        ac_div = 'inf'

    try:
        ca_div = c / a
    except:
        ca_div = 'inf'

    print("a / b =", ab_div)
    print("b / a =", ba_div)
    print("a / c =", ac_div)
    print("c / a =", ca_div)
