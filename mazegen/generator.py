from typing import Tuple, Iterator, Optional
from random import Random
from .constants import (
    ALL_WALLS,
    OPPOSITE_WALL,
    DIRECTION_OFFSETS,
    OFFSETS_42
)


class MazeGenerator:
    def __init__(self, width: int, height: int, entry: Tuple[int, int],
                 exit: Tuple[int, int], seed: Optional[int] = None) -> None:
        if width < 1 or height < 1:
            raise ValueError("Maze dimensions must be positive")
        if len(entry) != 2 or len(exit) != 2:
            raise ValueError("Entry and exit must each contain x,y coordinates")
        if entry == exit:
            raise ValueError("Entry and exit must be different cells")
        for name, (x, y) in (("Entry", entry), ("Exit", exit)):
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(f"{name} must be inside the maze bounds")

        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.rng = Random(seed)
        self.grid = [
            [ALL_WALLS for _ in range(self.width)]
            for _ in range(self.height)
        ]
        self.visited = set()
        self.stack = []
        self.pattern_42_cells = set()
        self._inject_42()

    def _get_unvisited_neighbors(self, x: int, y: int) -> list:
        neighbors = []
        for direction, (dx, dy) in DIRECTION_OFFSETS.items():
            next_x = x + dx
            next_y = y + dy

            if 0 <= next_x < self.width and 0 <= next_y < self.height:
                if (next_x, next_y) not in self.visited:
                    neighbors.append((direction, (next_x, next_y)))
        return neighbors

    def carve_path(self) -> Iterator[Tuple[int, int]]:
        start_x, start_y = self.entry

        self.visited.add((start_x, start_y))
        self.stack.append((start_x, start_y))

        while self.stack:
            curr_x, curr_y = self.stack[-1]
            unvisited = self._get_unvisited_neighbors(curr_x, curr_y)

            if unvisited:
                direction, (next_x, next_y) = self.rng.choice(unvisited)
                self.grid[curr_y][curr_x] &= ~direction

                opposite = OPPOSITE_WALL[direction]
                self.grid[next_y][next_x] &= ~opposite

                self.visited.add((next_x, next_y))
                self.stack.append((next_x, next_y))
            else:
                self.stack.pop()

            yield curr_x, curr_y

    def prim_path(self) -> Iterator[Tuple[int, int]]:
        start = self.entry
        self.visited.add(start)
        frontier = [
            (start, direction, neighbor)
            for direction, neighbor in self._get_unvisited_neighbors(*start)
        ]

        while frontier:
            source, direction, destination = self.rng.choice(frontier)
            frontier.remove((source, direction, destination))

            if destination in self.visited:
                continue

            source_x, source_y = source
            destination_x, destination_y = destination
            self.grid[source_y][source_x] &= ~direction
            opposite = OPPOSITE_WALL[direction]
            self.grid[destination_y][destination_x] &= ~opposite

            self.visited.add(destination)
            frontier.extend(
                (destination, next_direction, neighbor)
                for next_direction, neighbor in self._get_unvisited_neighbors(
                    destination_x, destination_y
                )
            )

            yield destination

    def _inject_42(self) -> None:
        if self.width < 9 or self.height < 7:
            print("Error: Maze size does not allow the '42' pattern.")
            return

        center_x = self.width // 2
        center_y = self.height // 2

        for offset_x, offset_y in OFFSETS_42:
            cell_x = center_x + offset_x
            cell_y = center_y + offset_y
            cell = (cell_x, cell_y)
            if cell == self.entry or cell == self.exit:
                raise ValueError("Entry and exit cannot be inside the 42 pattern")
            self.visited.add(cell)
            self.pattern_42_cells.add(cell)

    def braid(self) -> Iterator[Tuple[int, int]]:
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_42_cells:
                    continue
                
                if len(self._get_open_neighbors(x, y)) == 1:
                    
                    valid_walls = [
                        (direction, x + dx, y + dy)
                        for direction, (dx, dy) in DIRECTION_OFFSETS.items()
                        if 0 <= x + dx < self.width and 0 <= y + dy < self.height
                        and (x + dx, y + dy) not in self.pattern_42_cells
                        and self.grid[y][x] & direction
                    ]
                    
                    if valid_walls:
                        direction, next_x, next_y = self.rng.choice(valid_walls)
                        
                        self.grid[y][x] &= ~direction
                        self.grid[next_y][next_x] &= ~OPPOSITE_WALL[direction]
                        
                        yield x, y

    def _get_open_neighbors(self, x: int, y: int) -> list:
        return [
            (x + dx, y + dy)
            for direction, (dx, dy) in DIRECTION_OFFSETS.items()
            if 0 <= x + dx < self.width
            and 0 <= y + dy < self.height
            and not self.grid[y][x] & direction
        ]