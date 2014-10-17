"""
TESTS is a dict with all you tests.
Keys for this will be categories' names.
Each test is dict with
    "input" -- input data for user function
    "answer" -- your right answer
    "explanation" -- not necessary key, it's using for additional info in animation.
"""

TESTS = {
    "1. Simple": {
        "maze": [
            "XXXXXXXXXXXX",
            "X..........X",
            "X.XXXXXXXX.X",
            "X.X......X.X",
            "X.X......X.X",
            "X.X......X.X",
            "X.X......X.X",
            "X.X......X.X",
            "X.X......X.X",
            "X.XXXXXXXX.X",
            "X.........EX",
            "XXXXXXXXXXXX"
        ],
        "player": [1, 1]
    },
    "2. Second": {
        "maze": [
            "XXXXXXXXXXXX",
            "XX...X.....X",
            "X..X.X.X.X.X",
            "X.XX.X.X.X.X",
            "X..X.X.X.X.X",
            "XX.X.X.X.X.X",
            "X..X.X.X.X.X",
            "X.XX.X.X.X.X",
            "X..X.X.X.X.X",
            "XX.X.X.X.X.X",
            "XE.X.....X.X",
            "XXXXXXXXXXXX",
        ],
        "player": [10, 10]
    },
    "3. Left Rule": {
        "maze": [
            "XXXXXXXXXXXX",
            "X..........X",
            "X.XXXXXXXX.X",
            "X.X......X.X",
            "X.X.XX.X.X.X",
            "X.X......X.X",
            "X.X......X.X",
            "X.X..E...X.X",
            "X.X......X.X",
            "X.XXXX.XXX.X",
            "X..........X",
            "XXXXXXXXXXXX",
        ],
        "player": [1, 7]
    }
}

import random

DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1))
ALL_DIRECT = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1))


def neighbours(coor, maze, direct=DIRECTIONS):
    x, y = coor
    N = len(maze)
    res = []
    for d in direct:
        nx = x + d[0]
        ny = y + d[1]
        if 0 < nx < N - 1 and 0 < ny < N - 1:
            res.append((nx, ny))
    return res


def carve(coor, maze):
    maze[coor[0]][coor[1]] = "."


def isOpen(coor, maze):
    return maze[coor[0]][coor[1]] == "."


def generateMaze(N):
    maze = [["X"] * N for _ in range(N)]
    start = (1, 1)
    exit = (N - 2, N - 2)
    queue = [start]
    good_neighs = []
    while queue or good_neighs:
        if good_neighs:
            current = random.choice(good_neighs)
            queue.append(current)
        else:
            current = queue[-1]
        carve(current, maze)
        neighs = [n for n in neighbours(current, maze) if not isOpen(n, maze)]
        good_neighs = []
        for n in neighs:
            new_neighs = neighbours(n, maze, ALL_DIRECT)
            all_current_neighs = neighbours(current, maze)
            for cn in all_current_neighs:
                if cn in new_neighs:
                    new_neighs.remove(cn)
            if len([1 for x, y in new_neighs if maze[x][y] == "."]) <= 1:
                good_neighs.append(n)
        if not good_neighs:
            queue.remove(current)
    return maze


for i in range(4, 7):
    name = "{}. Random".format(i)
    maze = generateMaze(12)
    x = y = 0
    while maze[x][y] == "X":
        x, y = random.randint(1, 10), random.randint(1, 10)
    player = x, y
    row_edges = [1, 5] if x // 6 else [6, 10]
    col_edges = [1, 5] if y // 6 else [6, 10]
    x = y = 0
    while maze[x][y] == "X":
        x, y = random.randint(*row_edges), random.randint(*col_edges)
    maze[x][y] = "E"
    TESTS[name] = {"maze": tuple("".join(row) for row in maze), "player": player}
