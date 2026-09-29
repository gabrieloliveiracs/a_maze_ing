from mazegen import MazeGenerator
from mazegen import (
    ALL_WALLS,
    WALL_N, WALL_E, WALL_S, WALL_W,
    OPPOSITE_WALL,
    DIRECTION_OFFSETS
)


class MazeSolver:
    def __init__(self, maze: MazeGenerator, algorithm="dead-end-fill"):
        self.grid = maze.grid
        self.width = maze.width
        self.height = maze.height
        self.entry = maze.entry
        self.exit = maze.exit
        self.path = []

    def _get_open_neighbors(self, maze, x, y):
        open = []
        for direction, (dx, dy) in DIRECTION_OFFSETS.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if (maze[y][x] & direction) == 0:
                    open.append((direction, (nx, ny)))
        return open

    def _is_dead_end(self, maze, x, y):
        return len(self._get_open_neighbors(maze, x, y)) == 1

    def dead_end_fill(self):
        dead_ends = []

        for y in range(len(self.grid)):
            for x in range(len(self.grid[0])):
                if (x, y) == self.entry or (x, y) == self.exit:
                    continue

                if self._is_dead_end(self.grid, x, y):
                    dead_ends.append((x, y))

        while dead_ends:
            curr_x, curr_y = dead_ends.pop()

            neighbor = self._get_open_neighbors(self.grid, curr_x, curr_y)

            neighbor_direction, (nx, ny) = neighbor[0]

            self.grid[curr_y][curr_x] = ALL_WALLS

            opposite = OPPOSITE_WALL[neighbor_direction]
            self.grid[ny][nx] += opposite

            yield curr_x, curr_y

            if (nx, ny) != self.entry and (nx, ny) != self.exit:
                if self._is_dead_end(self.grid, nx, ny):
                    dead_ends.append((nx, ny))
