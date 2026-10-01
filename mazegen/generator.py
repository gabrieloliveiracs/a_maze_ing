from typing import Tuple, Iterator, Optional
from random import Random
from .constants import (
    ALL_WALLS,
    WALL_N, WALL_E, WALL_S, WALL_W,
    OPPOSITE_WALL,
    DIRECTION_OFFSETS,
    OFFSETS_42
)


class MazeGenerator:
    def __init__(self, width: int, height: int, entry: Tuple[int, int],
                 exit: Tuple[int, int], seed: Optional[int] = None) -> None:
        if width < 9 or height < 7:
            raise ValueError("Maze dimensions must be at least 9x7 to fit the 42 pattern")
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
        expected_visited = {
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
        }
        if self.visited != expected_visited:
            raise RuntimeError("Generate the maze before braiding it")

        loops = 0
        while True:
            dead_ends = self._get_real_dead_ends()
            if len(dead_ends) <= 2 and loops >= 2:
                return

            sources = dead_ends if len(dead_ends) > 2 else [
                (x, y)
                for y in range(self.height)
                for x in range(self.width)
                if (x, y) not in self.pattern_42_cells
            ]
            candidates = []
            for x, y in sources:
                for direction, (dx, dy) in DIRECTION_OFFSETS.items():
                    next_x, next_y = x + dx, y + dy
                    neighbor = (next_x, next_y)
                    if not (0 <= next_x < self.width and 0 <= next_y < self.height):
                        continue
                    if neighbor in self.pattern_42_cells:
                        continue
                    if not self.grid[y][x] & direction:
                        continue

                    self.grid[y][x] &= ~direction
                    opposite = OPPOSITE_WALL[direction]
                    self.grid[next_y][next_x] &= ~opposite
                    creates_open_area = self._has_open_3x3_area()
                    self.grid[y][x] |= direction
                    self.grid[next_y][next_x] |= opposite

                    if not creates_open_area:
                        candidates.append((x, y, direction, next_x, next_y))

            if not candidates:
                raise ValueError(
                    "Cannot satisfy playable-maze loop and dead-end limits "
                    "without opening a 3x3 area"
                )

            self.rng.shuffle(candidates)
            x, y, direction, next_x, next_y = candidates[0]
            self.grid[y][x] &= ~direction
            opposite = OPPOSITE_WALL[direction]
            self.grid[next_y][next_x] &= ~opposite
            loops += 1
            yield x, y

    def _get_real_dead_ends(self) -> list:
        dead_ends = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_42_cells:
                    continue
                if len(self._get_open_neighbors(x, y)) != 1:
                    continue

                has_openable_wall = any(
                    0 <= x + dx < self.width
                    and 0 <= y + dy < self.height
                    and (x + dx, y + dy) not in self.pattern_42_cells
                    and self.grid[y][x] & direction
                    for direction, (dx, dy) in DIRECTION_OFFSETS.items()
                )
                if has_openable_wall:
                    dead_ends.append((x, y))
        return dead_ends

    def _get_open_neighbors(self, x: int, y: int) -> list:
        return [
            (x + dx, y + dy)
            for direction, (dx, dy) in DIRECTION_OFFSETS.items()
            if 0 <= x + dx < self.width
            and 0 <= y + dy < self.height
            and not self.grid[y][x] & direction
        ]

    def _has_open_3x3_area(self) -> bool:
        for top_y in range(self.height - 2):
            for left_x in range(self.width - 2):
                if all(
                    not self.grid[y][x] & direction
                    for y in range(top_y, top_y + 3)
                    for x in range(left_x, left_x + 3)
                    for direction in (
                        ([WALL_E] if x < left_x + 2 else [])
                        + ([WALL_S] if y < top_y + 2 else [])
                    )
                ):
                    return True
        return False
