def pluck(arr):
    smallest_even = [float('inf'), -1]
    for i, num in enumerate(arr):
        if num % 2 == 0 and num < smallest_even[0]:
            smallest_even = [num, i]
    return smallest_even if smallest_even[1] != -1 else []
print(pluck([4,2,3]))  
print(pluck([1,2,3]))  
print(pluck([]))  
print(pluck([5, 0, 3, 0, 4, 2]))