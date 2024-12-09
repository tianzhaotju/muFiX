def select_words(s, n):
    vowels = 'aeiou'
    words = s.split()
    result = []
    for word in words:
        count = 0
        for letter in word:
            if letter.lower() not in vowels:
                count += 1
        if count == n:
            result.append(word)
    return result