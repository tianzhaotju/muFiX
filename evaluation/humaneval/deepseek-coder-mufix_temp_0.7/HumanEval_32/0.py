import math

def poly(xs: list, x: float):
    """
    Evaluates polynomial with coefficients xs at point x.
    return xs[0] + xs[1] * x + xs[1] * x^2 + .... xs[n] * x^n
    """
    return sum([coeff * math.pow(x, i) for i, coeff in enumerate(xs)])

def find_zero(xs: list):
    """
    xs are coefficients of a polynomial.
    find_zero find x such that poly(x) = 0.
    find_zero returns only only zero point, even if there are many.
    Moreover, find_zero only takes list xs having even number of coefficients and largest non zero coefficient as it guarantees a solution.
    """
    def bisection(a, b):
        if poly(a) * poly(b) > 0:
            return None
        c = a
        while (b-a) >= 0.01:
            c = (a+b)/2
            if poly(c) == 0.0:
                break
            else:
                if poly(a) * poly(c) < 0:
                    b = c
                else:
                    a = c
        return c

    max_coeff = max(abs(coeff) for coeff in xs)
    return bisection(-max_coeff, max_coeff)