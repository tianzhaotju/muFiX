def count_nums(arr):
    def sum_of_digits(n):
        s = 0
        while n:
            s += n % 10
            n //= 10
        return s
    return sum(sum_of_digits(abs(x)) > 0 for x in arr)