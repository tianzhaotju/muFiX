def change_base(x: int, base: int) -> str:
    """
    Change numerical base of input number x to base.
    return string representation after the conversion.
    base numbers are less than 10.

    Args:
    x (int): The number to be converted.
    base (int): The base to which the number is to be converted.

    Returns:
    str: The string representation of the number after the conversion.

    Examples:
    >>> change_base(8, 3)
    '22'
    >>> change_base(8, 2)
    '1000'
    >>> change_base(7, 2)
    '111'
    """
    if not 2 <= base <= 10:
        raise ValueError("Base must be between 2 and 10")
    if x == 0:
        return '0'
    digits = []
    while x:
        digits.append(str(x % base))
        x //= base
    return ''.join(digits[::-1])