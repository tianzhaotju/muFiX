def prime_fib(n: int):
    def is_prime(num: int) -> bool:
        if num < 2:
            return False
        for i in range(2, int(num**0.5) + 1):
            if num % i == 0:
                return False
        return True

    def fib(n: int) -> int:
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a

    i = 1
    prime_fib_numbers = []
    while len(prime_fib_numbers) < n:
        fib_number = fib(i)
        if is_prime(fib_number):
            prime_fib_numbers.append(fib_number)
        i += 1
    return prime_fib_numbers[-1]