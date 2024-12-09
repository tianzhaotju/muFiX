import heapq

def minPath(grid, k):
    n = len(grid)
    pq = [(grid[0][0], 0, 0)]
    visited = [[False]*n for _ in range(n)]
    visited[0][0] = True
    res = [grid[0][0]]
    while len(res) < k:
        _, x, y = heapq.heappop(pq)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < n and not visited[nx][ny]:
                visited[nx][ny] = True
                heapq.heappush(pq, (grid[nx][ny], nx, ny))
        res.append(pq[0][0])
    return res