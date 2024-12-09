def prod_signs(arr):
    if len(arr) == 0:
        return None
    sum_magnitude = 0
    product_sign = 1
    for num in arr:
        if num == 0:
            return 0
        sum_magnitude += abs(num)
        product_sign *= (1 if num > 0 else -1)
    return product_sign * sum_magnitude

<|EOT|>