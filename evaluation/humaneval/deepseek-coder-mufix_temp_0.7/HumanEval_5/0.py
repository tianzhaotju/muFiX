def intersperse(lst, delimiter):
    result = []
    for i in range(len(lst)):
        result.append(lst[i])
        if i < len(lst) - 1:  
            result.append(delimiter)
    return result
print(intersperse([], 4))  
print(intersperse([1, 2, 3], 4))