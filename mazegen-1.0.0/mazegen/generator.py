from typing import Iterator, List, Optional, Set, Tuple
from random import Random
from .constants import (
    ALL_WALLS,
    OPPOSITE_WALL,
    DIRECTION_OFFSETS,
    OFFSETS_42
)


class MazeGenerator:
    """Generate a maze using different path creation algorithms."""

    def __init__(self, width: int, height: int, entry: Tuple[int, int],
                 exit: Tuple[int, int], seed: Optional[int] = None) -> None:
        """Initialize the maze and validate its dimensions and positions.

        Args:
            width: The number of columns in the maze.
            height: The number of rows in the maze.
            entry: The starting cell coordinates (x, y).
            exit: The ending cell coordinates (x, y).
            seed: An optional value used to control random choices.

        Raises:
            ValueError: If the dimensions or positions are invalid,
                or if the maze is too small for the required pattern.
        """
        if width < 1 or height < 1:
            raise ValueError("Maze dimensions must be positive")
        if len(entry) != 2 or len(exit) != 2:
            raise ValueError(
                "Entry and exit must each contain x,y coordinates")
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
        self.visited: Set[Tuple[int, int]] = set()
        self.stack: List[Tuple[int, int]] = []
        self.pattern_42_cells: Set[Tuple[int, int]] = set()
        self._inject_42()

    def _get_unvisited_neighbors(self, x: int, y: int) -> list:
        """Find neighboring cells that have not been visited.

        Args:
            x: The column index of the current cell.
            y: The row index of the current cell.

        Returns:
            A list of directions and coordinates for unvisited neighbors.
        """
        neighbors = []
        for direction, (dx, dy) in DIRECTION_OFFSETS.items():
            next_x = x + dx
            next_y = y + dy

            if 0 <= next_x < self.width and 0 <= next_y < self.height:
                if (next_x, next_y) not in self.visited:
                    neighbors.append((direction, (next_x, next_y)))
        return neighbors

    def carve_path(self) -> Iterator[Tuple[int, int]]:
        """Create maze paths using depth-first search.

        Start at the entry cell and visit unvisited neighbors in random
        order. Remove the walls between connected cells and return to
        previous cells when no unvisited neighbors remain.

        Yields:
            The coordinates of each cell processed by the algorithm.
        """
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
        """Create maze paths using a randomized version of Prim's algorithm.

        Start at the entry cell and keep a list of possible connections
        to unvisited cells. Randomly select connections and remove walls
        until no more cells can be reached.

        Yields:
            The coordinates of each newly visited cell.
        """
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
        """Place the required '42' pattern in the center of the maze.

        Mark the pattern cells as visited so that the path algorithms
        do not treat them as normal unvisited cells.

        Raises:
            ValueError: If the maze is too small or the entry or exit
                is inside the pattern.
        """
        if self.width < 9 or self.height < 7:
            raise ValueError(
                "Maze dimensions are too small for the required '42' pattern "
                "(minimum 9 columns by 7 rows)"
            )

        center_x = self.width // 2
        center_y = self.height // 2

        for offset_x, offset_y in OFFSETS_42:
            cell_x = center_x + offset_x
            cell_y = center_y + offset_y
            cell = (cell_x, cell_y)
            if cell == self.entry or cell == self.exit:
                raise ValueError(
                    "Entry and exit cannot be inside the 42 pattern")
            self.visited.add(cell)
            self.pattern_42_cells.add(cell)

    def braid(self) -> Iterator[Tuple[int, int]]:
        """Add extra connections to reduce dead ends in the maze.

        Check each cell and open a random wall when the cell has only
        one open neighboring connection. Do not modify cells that
        belong to the '42' pattern.

        Yields:
            The coordinates of each cell where a wall was removed.
        """
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_42_cells:
                    continue

                if len(self._get_open_neighbors(x, y)) == 1:

                    valid_walls = [
                        (direction, x + dx, y + dy)
                        for direction, (dx, dy) in DIRECTION_OFFSETS.items()
                        if (
                            0 <= x + dx < self.width
                            and 0 <= y + dy < self.height
                        )
                        and (x + dx, y + dy) not in self.pattern_42_cells
                        and self.grid[y][x] & direction
                    ]

                    if valid_walls:
                        direction, next_x, next_y = self.rng.choice(
                            valid_walls)

                        self.grid[y][x] &= ~direction
                        self.grid[next_y][next_x] &= ~OPPOSITE_WALL[direction]

                        yield x, y

    def _get_open_neighbors(self, x: int, y: int) -> list:
        """Find neighboring cells connected to the current cell.

        Args:
            x: The column index of the current cell.
            y: The row index of the current cell.

        Returns:
            A list of coordinates for neighboring cells connected
            through open walls.
        """
        return [
            (x + dx, y + dy)
            for direction, (dx, dy) in DIRECTION_OFFSETS.items()
            if 0 <= x + dx < self.width
            and 0 <= y + dy < self.height
            and not self.grid[y][x] & direction
        ]
