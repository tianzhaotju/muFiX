def flip_case(string: str) -> str:
    """
    For a given string, flip lowercase characters to uppercase and uppercase to lowercase.

    Args:
    string (str): The input string.

    Returns:
    str: The flipped case string.

    Examples:
    >>> flip_case('Hello')
    'hELLO'
    """
    return ''.join([char.upper() if char.islower() else char.lower() for char in string])