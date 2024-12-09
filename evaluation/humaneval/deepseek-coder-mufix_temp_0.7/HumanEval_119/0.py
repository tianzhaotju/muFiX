def match_parens(lst):
    left = lst[0].count('(')
    right = lst[1].count(')')
    
    if left < right:
        lst[0] += ')' * (right - left)
    else:
        lst[1] += '(' * (left - right)
        
    combined = lst[0] + lst[1]
    stack = []

    for p in combined:
        if p == '(':
            stack.append(p)
        else:
            if not stack:
                return 'No'
            stack.pop()

    return 'Yes' if not stack else 'No'