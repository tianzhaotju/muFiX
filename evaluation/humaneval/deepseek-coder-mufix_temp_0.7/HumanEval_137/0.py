def compare_one(a, b):
    """
    Create a function that takes integers, floats, or strings representing real numbers, and returns the larger variable in its given variable type.
    Return None if the values are equal.
    Note: If a real number is represented as a string, the floating point might be . or ,
    """
    # Check if both are strings and replace ',' with '.'
    if isinstance(a, str) and isinstance(b, str):
        a = float(a.replace(',', '.'))
        b = float(b.replace(',', '.'))

    # Check if one is string and replace ',' with '.'
    elif isinstance(a, str):
        a = float(a.replace(',', '.'))
    elif isinstance(b, str):
        b = float(b.replace(',', '.'))

    # Compare the values and return the larger one or None if they are equal
    if a > b:
        return a
    elif b > a:
        return b
    else:
        return None