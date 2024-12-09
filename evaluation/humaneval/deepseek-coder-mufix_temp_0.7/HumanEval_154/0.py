def cycpattern_check(a , b):
    """
    You are given 2 words. You need to return True if the second word or any of its rotations is a substring in the first word
    cycpattern_check("abcd","abd") => False
    cycpattern_check("hello","ell") => True
    cycpattern_check("whassup","psus") => False
    cycpattern_check("abab","baa") => True
    cycpattern_check("efef","eeff") => False
    cycpattern_check("himenss","simen") => True
    """
    # Check if b is a substring of a
    if b in a:
        return True

    # Check if any rotation of b is a substring of a
    for i in range(len(b)):
        if b[i:] + b[:i] in a:
            return True

    return False