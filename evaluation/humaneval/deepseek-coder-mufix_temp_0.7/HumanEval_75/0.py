def is_multiply_prime(n):
    def is_prime(num):
        if num < 2:
            return False
        for i in range(2, int(num**0.5) + 1):
            if num % i == 0:
                return False
        return True

    primes = [i for i in range(2, n) if is_prime(i)]
    count = 0
    for prime in primes:
        while n % prime == 0:
            n /= prime
            count += 1
            if count > 3:
                return False
    return count == 3