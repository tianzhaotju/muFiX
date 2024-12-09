def histogram(test):
    """Given a string representing a space separated lowercase letters, return a dictionary
    of the letter with the most repetition and containing the corresponding count.
    If several letters have the same occurrence, return all of them.
    
    Example:
    histogram('a b c') == {'a': 1, 'b': 1, 'c': 1}
    histogram('a b b a') == {'a': 2, 'b': 2}
    histogram('a b c a b') == {'a': 2, 'b': 2}
    histogram('b b b b a') == {'b': 4}
    histogram('') == {}

    """
    # Split the string into a list of words
    words = test.split()

    # Create an empty dictionary to store the counts
    counts = {}

    # Iterate over the words
    for word in words:
        # If the word is already in the dictionary, increment its count
        if word in counts:
            counts[word] += 1
        # Otherwise, add it to the dictionary with a count of 1
        else:
            counts[word] = 1

    # Find the maximum count
    max_count = max(counts.values()) if counts else 0

    # Create a new dictionary to store the results
    result = {k: v for k, v in counts.items() if v == max_count}

    return result