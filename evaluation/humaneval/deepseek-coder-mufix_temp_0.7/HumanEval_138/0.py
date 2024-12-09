def is_equal_to_sum_even(n):
    if n < 8 or n % 2 != 0:
        return False
    for i in range(2, n//2+1, 2):
        for j in range(i, n//2+1, 2):
            for k in range(j, n//2+1, 2):
                for l in range(k, n//2+1, 2):
                    if i + j + k + l == n:
                        return True
    return False
print(is_equal_to_sum_even(8))  
print(is_equal_to_sum_even(10))  
print(is_equal_to_sum_even(12))  
print(is_equal_to_sum_even(14))  
print(is_equal_to_sum_even(16))