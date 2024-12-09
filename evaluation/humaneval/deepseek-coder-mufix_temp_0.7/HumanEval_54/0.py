def same_chars(s0: str, s1: str):
    """
    Check if two words have the same characters.
    """
    # Remove all spaces from the strings
    s0 = s0.replace(' ', '')
    s1 = s1.replace(' ', '')

    # Sort the characters in the strings
    s0 = sorted(s0)
    s1 = sorted(s1)

    # Compare the sorted strings
    return s0 == s1