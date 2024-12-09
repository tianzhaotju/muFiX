def is_simple_power(x, n):
    """
    This function checks if a number x is a simple power of n.
    A number x is a simple power of n if n**int=x.
    For example:
    is_simple_power(1, 4) => True
    is_simple_power(2, 2) => True
    is_simple_power(8, 2) => True
    is_simple_power(3, 2) => False
    is_simple_power(3, 1) => False
    is_simple_power(5, 3) => False
    """
    if x == 1:
        return True
    if n == 1:
        return False
    i = 2
    while i <= x:
        if i**n == x:
            return True
        i += 1
    return False