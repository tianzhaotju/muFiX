def match_parens(lst):
    '''
    You are given a list of two strings, both strings consist of open
    parentheses '(' or close parentheses ')' only.
    Your job is to check if it is possible to concatenate the two strings in
    some order, that the resulting string will be good.
    A string S is considered to be good if and only if all parentheses in S
    are balanced. For example: the string '(())()' is good, while the string
    '())' is not.
    Return 'Yes' if there's a way to make a good string, and return 'No' otherwise.

    Examples:
    match_parens(['()(', ')']) == 'Yes'
    match_parens([')', ')']) == 'No'
    '''
    # Initialize a counter for open and close parentheses
    open_count = 0
    close_count = 0

    # Iterate over the first string in the list
    for char in lst[0]:
        if char == '(':
            open_count += 1
        else:
            if open_count > 0:
                open_count -= 1
            else:
                close_count += 1

    # Iterate over the second string in the list
    for char in lst[1]:
        if char == '(':
            open_count += 1
        else:
            if open_count > 0:
                open_count -= 1
            else:
                close_count += 1

    # If there are more close parentheses than open parentheses,
    # we can balance the parentheses by adding open parentheses
    if close_count > open_count:
        return 'Yes'

    # If there are more open parentheses than close parentheses,
    # we can balance the parentheses by adding close parentheses
    if open_count > close_count:
        return 'Yes'

    # If there are equal number of open and close parentheses,
    # we can balance the parentheses by adding either
    return 'Yes'