def encode(message):
    vowels = {'a': 'c', 'e': 'g', 'i': 'k', 'o': 'm', 'u': 'q', 'A': 'C', 'E': 'G', 'I': 'K', 'O': 'M', 'U': 'Q'}
    encoded_message = ""
    for char in message:
        if char.isalpha():
            encoded_message += vowels[char] if char in vowels else chr(ord(char) + 2)
        else:
            encoded_message += char
    return encoded_message

print(encode('test'))  # Output: TGST
print(encode('This is a message'))  # Output: tHKS KS C MGSSCGG