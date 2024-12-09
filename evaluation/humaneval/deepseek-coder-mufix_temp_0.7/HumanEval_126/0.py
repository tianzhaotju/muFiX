def is_sorted(lst):
    '''
    Given a list of numbers, return whether or not they are sorted in ascending order.
    If list has more than 1 duplicate of the same number, return False.
    Assume no negative numbers and only integers.
    '''

    for i in range(len(lst) - 1):
        if lst[i] >= lst[i + 1]:
            return False

    # Check for duplicates
    duplicates = [item for item in lst if lst.count(item) > 1]
    if len(duplicates) > 0:
        return False

    return True