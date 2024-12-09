def tri(n):
    """
    Everyone knows Fibonacci sequence, it was studied deeply by mathematicians in 
    the last couple centuries. However, what people don't know is Tribonacci sequence.
    Tribonacci sequence is defined by the recurrence:
    tri(1) = 3
    tri(n) = 1 + n / 2, if n is even.
    tri(n) =  tri(n - 1) + tri(n - 2) + tri(n + 1), if n is odd.
    For example:
    tri(2) = 1 + (2 / 2) = 2
    tri(4) = 3
    tri(3) = tri(2) + tri(1) + tri(4)
           = 2 + 3 + 3 = 8 
    You are given a non-negative integer number n, you have to a return a list of the 
    first n + 1 numbers of the Tribonacci sequence.
    Examples:
    tri(3) = [1, 3, 2, 8]
    """
    if n < 0:
        return []
    tri_seq = [1, 3, 2]
    while len(tri_seq) <= n:
        if len(tri_seq) % 2 == 0:
            tri_seq.append(1 + len(tri_seq) // 2)
        else:
            tri_seq.append(tri_seq[-1] + tri_seq[-2] + tri_seq[-3])
    return tri_seq[:n+1]