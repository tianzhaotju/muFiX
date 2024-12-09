def choose_num(x, y):
    """
    This function takes two positive numbers x and y and returns the
    biggest even integer number that is in the range [x, y] inclusive. If 
    there's no such number, then the function should return -1.

    For example:
    choose_num(12, 15) returns 14
    choose_num(13, 12) returns -1
    """
    if x > y:
        return -1
    elif x % 2 == 0:
        return y if y % 2 == 0 else y - 1
    else:
        return y if y % 2 == 0 else y - 1 if y - 1 > x else -1