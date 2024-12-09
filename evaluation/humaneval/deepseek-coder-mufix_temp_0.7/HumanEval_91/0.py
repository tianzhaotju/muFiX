def is_bored(S):
    """
    You'll be given a string of words, and your task is to count the number of boredoms.
    A boredom is a sentence that starts with the word "I".
    Sentences are delimited by '.', '?' or '!'.
    """
    # split the string S into sentences
    sentences = [sentence.strip() for sentence in S.replace("?!", "?").split(".") if sentence.strip()]

    # count the number of sentences that start with "I"
    return sum(1 for sentence in sentences if sentence.startswith("I"))