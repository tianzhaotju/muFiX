from typing import List

def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """
    Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.

    Args:
    numbers (List[float]): List of numbers to check.
    threshold (float): Threshold value.

    Returns:
    bool: True if any two numbers in the list are closer to each other than the threshold, False otherwise.

    Examples:
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """
    numbers.sort()
    for i in range(1, len(numbers)):
        if numbers[i] - numbers[i - 1] < threshold:
            return True
    return False