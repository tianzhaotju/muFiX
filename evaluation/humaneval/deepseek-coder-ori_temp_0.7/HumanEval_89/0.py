def encrypt(s):
    """
    Create a function encrypt that takes a string as an argument and
    returns a string encrypted with the alphabet being rotated. 
    The alphabet should be rotated in a manner such that the letters 
    shift down by two multiplied to two places.
    For example:
    encrypt('hi') returns 'lm'
    encrypt('asdfghjkl') returns 'ewhjklnop'
    encrypt('gf') returns 'kj'
    encrypt('et') returns 'ix'
    """
    encrypted_s = ""
    for char in s:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            encrypted_s += chr((ord(char) - ascii_offset + 2*2) % 26 + ascii_offset)
        else:
            encrypted_s += char
    return encrypted_s