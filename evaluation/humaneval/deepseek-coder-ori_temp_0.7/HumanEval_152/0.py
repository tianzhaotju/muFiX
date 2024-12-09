def compare(game, guess):
    """
    This function takes two lists of equal length as input. Each index in the lists represents a match. 
    The function returns a list of the same length where each index shows how far off the guess was. 
    If the guess was correct, the value is 0. If not, the value is the absolute difference between the guess and the score.

    Example:

    compare([1,2,3,4,5,1],[1,2,3,4,2,-2]) -> [0,0,0,0,3,3]
    compare([0,5,0,0,0,4],[4,1,1,0,0,-2]) -> [4,4,1,0,0,6]
    """
    return [abs(g - h) for g, h in zip(game, guess)]