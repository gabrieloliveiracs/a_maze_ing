from .config import Config
from random import choice
from constants import (
    ALL_WALLS, 
    WALL_N, WALL_E, WALL_S, WALL_W, 
    OPPOSITE_WALL, 
    DIRECTION_OFFSETS
)
class Mazegenerator:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.grid = [
            [ALL_WALLS for _ in range(self.config.width)]
            for _ in range(self.config.height)
            ]
        self.visited = set()
        self.stack = []

    def _get_unvisited_neighbors(self, x: int, y: int) -> list:
        neighbors = []
        for direction, (dx, dy) in DIRECTION_OFFSETS.items():
            next_x = x + dx
            next_y = y + dy

            if 0 <= next_x < self.config.width and 0 <= next_y < self.config.height:
                if (next_x, next_y) not in self.visited:
                    neighbors.append((direction, (next_x, next_y)))
        return neighbors

    def carve_path(self) -> None:
        start_x, start_y = self.config.entry

        self.visited.add((start_x, start_y))
        self.stack.append((start_x, start_y))

        while len(self.stack) > 0:
            curr_x, curr_y = self.stack[-1]

            unvisited = self._get_unvisited_neighbors(curr_x, curr_y)

            if unvisited:
                direction, (next_x, next_y) = choice(unvisited)

                self.grid[curr_y][curr_x] &= ~direction

                opposite = OPPOSITE_WALL[direction]
                self.grid[next_y][next_x] &= ~opposite

                self.visited.add((next_x, next_y))
                self.stack.append((next_x, next_y))
            else:
                self.stack.pop()

