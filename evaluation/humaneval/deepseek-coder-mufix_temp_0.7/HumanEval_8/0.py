from typing import List, Tuple

def sum_product(numbers: List[int]) -> Tuple[int, int]:
    """ 
    For a given list of integers, return a tuple consisting of a sum and a product of all the integers in a list.
    Empty sum should be equal to 0 and empty product should be equal to 1.
    
    Args:
    numbers (List[int]): List of integers.

    Returns:
    Tuple[int, int]: A tuple consisting of sum and product of all integers in the list.

    Examples:
    >>> sum_product([])
    (0, 1)
    >>> sum_product([1, 2, 3, 4])
    (10, 24)
    """
    sum_numbers = 0
    product_numbers = 1
    for num in numbers:
        sum_numbers += num
        product_numbers *= num
    return (sum_numbers, product_numbers)