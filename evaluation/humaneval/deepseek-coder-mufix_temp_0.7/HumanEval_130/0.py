def tri(n):
    if n == 0:
        return [1]
    elif n == 1:
        return [1, 3]
    elif n == 2:
        return [1, 3, 2]
    else:
        sequence = [1, 3, 2]
        for i in range(3, n+1):
            if sequence[i-1] % 2 == 0:
                sequence.append(1 + sequence[i-1] // 2)
            else:
                sequence.append(sequence[i-2] + sequence[i-1] + sequence[i])
        return sequence