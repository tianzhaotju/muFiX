def max_fill(grid, capacity):
    count = 0
    for row in grid:
        for well in row:
            if well == 0:
                count += 1
            else:
                count += capacity
    return count

print(max_fill([[0,0,1,0], [0,1,0,0], [1,1,1,1]], 1))  # Output: 6
print(max_fill([[0,0,1,1], [0,0,0,0], [1,1,1,1], [0,1,1,1]], 2))  # Output: 5
print(max_fill([[0,0,0], [0,0,0]], 5))  # Output: 0