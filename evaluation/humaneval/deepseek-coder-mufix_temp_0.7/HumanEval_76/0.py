def is_simple_power(x, n):
    """Your task is to write a function that returns true if a number x is a simple power of n and false in other cases.
    x is a simple power of n if n**int=x
    """
    if n == 1:
        return x == 1
    while x > 1:
        x /= n
        if x == int(x):
            return True
    return False