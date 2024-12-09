def hex_key(num):
    """
    This function receives a hexadecimal number as a string and counts the number of hexadecimal 
    digits that are primes.

    Parameters:
    num (str): A hexadecimal number as a string.

    Returns:
    int: The number of hexadecimal digits that are primes.

    Examples:
    >>> hex_key("AB")
    1
    >>> hex_key("1077E")
    2
    >>> hex_key("ABED1A33")
    4
    >>> hex_key("123456789ABCDEF0")
    6
    >>> hex_key("2020")
    2
    """
    prime_hex_digits = {'2', '3', '5', '7', 'B', 'D'}
    return sum(1 for digit in num if digit in prime_hex_digits)