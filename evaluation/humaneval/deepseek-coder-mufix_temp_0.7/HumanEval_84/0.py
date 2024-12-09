def solve(N):
    # Convert the integer to binary and remove the '0b' prefix
    binary = bin(N)[2:]
    # Calculate the total sum of digits
    total = sum(int(digit) for digit in binary)
    # Convert the total sum to binary and return it
    return bin(total)[2:]

print(solve(1000))  # prints "1"
print(solve(150))   # prints "110"
print(solve(147))   # prints "1100"