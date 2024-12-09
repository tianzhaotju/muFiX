def is_palindrome(text: str) -> bool:
    """
    Checks if given string is a palindrome

    Args:
    text (str): The string to be checked

    Returns:
    bool: True if the string is a palindrome, False otherwise

    Examples:
    >>> is_palindrome('')
    True
    >>> is_palindrome('aba')
    True
    >>> is_palindrome('aaaaa')
    True
    >>> is_palindrome('zbcd')
    False
    """
    return text == text[::-1]