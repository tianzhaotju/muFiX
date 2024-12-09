def reverse_delete(s, c):
    # Delete all the characters in s that are equal to any character in c
    for char in c:
        s = s.replace(char, '')

    # Check if the result string is palindrome
    is_palindrome = s == s[::-1]

    # Return a tuple containing the result string and the check result
    return (s, is_palindrome)