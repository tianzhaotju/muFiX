from typing import List

def intersperse(numbers: List[int], delimeter: int) -> List[int]:
    """
    Insert a number 'delimeter' between every two consecutive elements of input list `numbers'
    
    Args:
    numbers (List[int]): The input list of integers.
    delimeter (int): The number to be inserted between consecutive elements.

    Returns:
    List[int]: The modified list with 'delimeter' inserted between every two consecutive elements.

    Examples:
    
    >>> intersperse([], 4)
    []
    >>> intersperse([1, 2, 3], 4)
    [1, 4, 2, 4, 3]
    """