def simplify(x, n):
    from fractions import Fraction
    x = Fraction(x)
    n = Fraction(n)
    return (x * n).denominator == 1