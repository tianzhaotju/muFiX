def string_sequence(n: int) -> str:
    """
    Return a string containing space-delimited numbers starting from 0 upto n inclusive.
    
    Parameters:
    n (int): The upper limit of the sequence.

    Returns:
    str: A string containing space-delimited numbers from 0 to n.

    Examples:
    
    >>> string_sequence(0)
    '0'
    >>> string_sequence(5)
    '0 1 2 3 4 5'
    """
    return ' '.join(str(i) for i in range(n+1))