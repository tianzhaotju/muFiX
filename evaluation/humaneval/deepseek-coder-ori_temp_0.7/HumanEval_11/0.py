from typing import List

def string_xor(a: str, b: str) -> str:
    """
    Input are two strings a and b consisting only of 1s and 0s.
    Perform binary XOR on these inputs and return result also as a string.

    >>> string_xor('010', '110')
    '100'
    """
    # Convert the strings to integers
    a = int(a, 2)
    b = int(b, 2)

    # Perform XOR operation
    result = a ^ b

    # Convert the result back to binary and return as a string
    return bin(result)[2:]