def is_nested(string):
    stack = []
    bracket_pairs = {'[': ']'}  # we only need to check for one type of brackets
    for bracket in string:
        if bracket in bracket_pairs:
            stack.append(bracket)
        else:
            if not stack:
                return False
            if bracket != bracket_pairs[stack.pop()]:
                return False
    return not stack  # return True if stack is empty, False otherwise

print(is_nested('[[]]'))  # True
print(is_nested('[]]]]]]][[[[[]'))  # False
print(is_nested('[][]'))  # False
print(is_nested('[]'))  # False
print(is_nested('[[][]]'))  # True
print(is_nested('[[]][['))  # False