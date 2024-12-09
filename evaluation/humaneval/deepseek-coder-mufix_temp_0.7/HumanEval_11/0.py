def string_xor(s1, s2):
    if len(s1) != len(s2):
        raise ValueError("Strings must be of the same length")
    return ''.join(str(int(a) ^ int(b)) for a, b in zip(s1, s2))
print(string_xor('010', '110'))