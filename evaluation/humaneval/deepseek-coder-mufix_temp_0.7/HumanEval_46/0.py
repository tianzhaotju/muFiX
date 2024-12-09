def fib4(n: int):
    if n == 0:
        return 0
    elif n == 1:
        return 0
    elif n == 2:
        return 2
    elif n == 3:
        return 0

    fibs = [0, 0, 2, 0]
    for i in range(4, n+1):
        fibs.append(fibs[i-1] + fibs[i-2] + fibs[i-3] + fibs[i-4])
    return fibs[n]