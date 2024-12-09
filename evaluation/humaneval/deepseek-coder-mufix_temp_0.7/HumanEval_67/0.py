def fruit_distribution(s,n):
    apples = int(s.split(" apples ")[0].split(" and ")[1])
    oranges = int(s.split(" oranges ")[0].split(" apples ")[1])
    return n - (apples + oranges)