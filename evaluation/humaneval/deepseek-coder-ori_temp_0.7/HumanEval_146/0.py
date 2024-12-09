def specialFilter(nums):
    """
    Write a function that takes an array of numbers as input and returns 
    the number of elements in the array that are greater than 10 and both 
    first and last digits of a number are odd (1, 3, 5, 7, 9).
    For example:
    specialFilter([15, -73, 14, -15]) => 1 
    specialFilter([33, -2, -3, 45, 21, 109]) => 2
    """
    count = 0
    for num in nums:
        if num > 10:
            str_num = str(abs(num))  # convert to string to easily access digits
            if int(str_num[0]) in [1, 3, 5, 7, 9] and int(str_num[-1]) in [1, 3, 5, 7, 9]:
                count += 1
    return count

print(specialFilter([15, -73, 14, -15]))  # Output: 1
print(specialFilter([33, -2, -3, 45, 21, 109]))  # Output: 2