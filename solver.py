from typing import Dict, Iterator, List, Optional, Tuple

from mazegen import MazeGenerator
from mazegen import (
    ALL_WALLS,
    OPPOSITE_WALL,
    DIRECTION_OFFSETS,
)


class MazeSolver:
    """Solve a generated maze and expose progress for animation.

    Args:
        maze: Generated maze to solve.
    """

    def __init__(self, maze: MazeGenerator) -> None:
        self.grid = maze.grid
        self.width = maze.width
        self.height = maze.height
        self.entry = maze.entry
        self.exit = maze.exit
        self.path: List[Tuple[int, int]] = []

    def _get_open_neighbors(
        self, maze: List[List[int]], x: int, y: int
    ) -> List[Tuple[int, Tuple[int, int]]]:
        open_neighbors = []
        for direction, (dx, dy) in DIRECTION_OFFSETS.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if (maze[y][x] & direction) == 0:
                    open_neighbors.append((direction, (nx, ny)))
        return open_neighbors

    def _is_dead_end(self, maze: List[List[int]], x: int, y: int) -> bool:
        return len(self._get_open_neighbors(maze, x, y)) == 1

    def dead_end_fill(self) -> Iterator[Tuple[int, int]]:
        """Remove dead ends from a temporary copy of the maze.

        The original grid is restored after the traversal completes.

        Yields:
            Coordinates of cells removed during dead-end filling.

        Returns:
            An iterator over eliminated cell coordinates.
        """
        dead_ends = []

        original_grid = [row[:] for row in self.grid]

        for y in range(len(self.grid)):
            for x in range(len(self.grid[0])):
                if (x, y) == self.entry or (x, y) == self.exit:
                    continue

                if self._is_dead_end(self.grid, x, y):
                    dead_ends.append((x, y))

        while dead_ends:
            curr_x, curr_y = dead_ends.pop()

            neighbors = self._get_open_neighbors(self.grid, curr_x, curr_y)

            neighbor_direction, (nx, ny) = neighbors[0]

            self.grid[curr_y][curr_x] = ALL_WALLS

            opposite = OPPOSITE_WALL[neighbor_direction]
            self.grid[ny][nx] += opposite

            yield curr_x, curr_y

            if (nx, ny) != self.entry and (nx, ny) != self.exit:
                if self._is_dead_end(self.grid, nx, ny):
                    dead_ends.append((nx, ny))

        self.path = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] != ALL_WALLS:
                    self.path.append((x, y))

        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = original_grid[y][x]

    def solver_bfs(self) -> Iterator[Tuple[int, int]]:
        """Find the shortest path with breadth-first search.

        The resulting path is stored in ``self.path``.

        Yields:
            Coordinates as they are visited before reaching the exit.

        Returns:
            An iterator over visited cell coordinates.
        """
        queue = [self.entry]

        came_from: Dict[
            Tuple[int, int], Optional[Tuple[int, int]]
        ] = {self.entry: None}

        while queue:
            current = queue.pop(0)

            if current == self.exit:
                break

            curr_x, curr_y = current
            open_neighbors = self._get_open_neighbors(
                self.grid, curr_x, curr_y)

            yield curr_x, curr_y

            for direction, (nx, ny) in open_neighbors:
                neighbor = (nx, ny)

                if neighbor not in came_from:
                    queue.append(neighbor)
                    came_from[neighbor] = current

        self.path = []
        path_current: Optional[Tuple[int, int]] = self.exit

        while path_current is not None:
            self.path.append(path_current)
            path_current = came_from.get(path_current)

        self.path.reverse()
