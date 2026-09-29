from typing import Tuple, Iterator
from random import choice
from .constants import (
    ALL_WALLS,
    WALL_N, WALL_E, WALL_S, WALL_W,
    OPPOSITE_WALL,
    DIRECTION_OFFSETS,
    OFFSETS_42
)


class MazeGenerator:
    def __init__(self, width: int, height: int, entry: Tuple[int, int],
                 exit: Tuple[int, int]) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
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

            yield (curr_x, curr_y)

    def _inject_42(self) -> None:
        """Um '42' visível, formado por células fechadas"""
        if self.width < 9 or self.height < 7:
            print("Error: Maze size does not allow the '42' pattern.")
        else:
            center_x = self.width // 2
            center_y = self.height // 2

            for offset_x, offset_y in OFFSETS_42:
                cell_x = center_x + offset_x
                cell_y = center_y + offset_y

                self.visited.add((cell_x, cell_y))
                self.pattern_42_cells.add((cell_x, cell_y))

    # def braid(self) -> Iterator[Tuple[int, int]]:
        # pra cada celula:
        #     se for entry, exit ou 42:
        #         pula

        #     se a célula tiver 3 paredes:
        #         lista os vizinhos validos (entre 0 e width e height e fora do 42", usar direction offsets)

        #         se tem vizinho valido
        #             choice(vizinho)
        #             quebra a parede entre a celula atual e esse vizinho
        #     (yield) cell atual
