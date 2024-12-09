def digits(n):
    product = 1
    is_odd = False

    while n:
        digit = n % 10
        if digit % 2 != 0:
            product *= digit
            is_odd = True
        n //= 10

    if is_odd:
        return product
    else:
        return 0