from typing import List, Tuple
from mazegen.constants import DIRECTION_OFFSETS
from config import Config

Coordinate = Tuple[int, int]
MazeGrid = List[List[int]]


class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'

    START = '\033[42m\033[30m'
    END = '\033[41m\033[30m'
    PATH = '\033[43m\033[30m'

    WALLS = [
        '\033[36m',
        '\033[94m',
        '\033[95m',
        '\033[37m',
        '\033[32m'
    ]

    NUMBER_42 = '\033[31m\033[0m'

    EXPLORER = '\033[102m\033[30m'
    TRAIL = '\033[100m'


class Symbols:
    WALL_BLOCK = "██"
    EMPTY = "  "
    START_POINT = f"{Colors.START}SS{Colors.RESET}"
    EXIT_POINT = f"{Colors.START}EE{Colors.RESET}"
    PATH_TRAIL = f"{Colors.START}..{Colors.RESET}"


class ASCIIRenderer:
    def __init__(
        self,
        grid: MazeGrid,
        entry: Coordinate,
        exit_point: Coordinate,
        path: List[Coordinate],
        config: Config
    ) -> None:
        self.grid = grid
        self.entry = entry
        self.exit_point = exit_point
        self.path = path
        self.config = config
        self.show_path = True
        self.color_idx = 0
        self.visited = None
        self.current_cell = None
<<<<<<< HEAD
        self.stack = None        
        self.pattern_42_cells = set()
=======
        self.stack = None
>>>>>>> 7634a45 (;)

        self.mask_north = 0
        self.mask_south = 0
        self.mask_east = 0
        self.mask_west = 0
        self._map_directional_masks()

    def _map_directional_masks(self) -> None:
        for wall_mask, (dx, dy) in DIRECTION_OFFSETS.items():
            if dy < 0:
                self.mask_north = wall_mask
            elif dy > 0:
                self.mask_south = wall_mask
            elif dx > 0:
                self.mask_east = wall_mask
            elif dx < 0:
                self.mask_west = wall_mask

    def _has_wall(self, cell_value: int, direction_mask: int) -> bool:
        return bool(cell_value & direction_mask)

    def _create_blank_expanded_grid(self, wall_char: str) -> List[List[str]]:
        maze_height, maze_width = len(self.grid), len(self.grid[0])
        expanded_width = (2 * maze_width) + 1
        expanded_height = (2 * maze_height) + 1

        return [[wall_char for _ in range(expanded_width)] for _ in range(expanded_height)]

    def _get_cell_visual(self, coord: Coordinate) -> str:
        if self.current_cell is not None and coord == self.current_cell:
            return f"{Colors.EXPLORER}  {Colors.RESET}"
        if self.stack is not None and coord in self.stack:
            return f"{Colors.TRAIL}  {Colors.RESET}"
        if coord == self.entry:
            return Symbols.START_POINT
        if coord == self.exit_point:
            return Symbols.EXIT_POINT
        if coord in self.path and self.show_path:
            return Symbols.PATH_TRAIL

        return Symbols.EMPTY

    def render(self) -> None:
        current_wall_color = Colors.WALLS[self.color_idx]
        wall_char = f"{current_wall_color}{Symbols.WALL_BLOCK}{Colors.RESET}"

        maze_height, maze_width = len(self.grid), len(self.grid[0])
        expanded_width = (2 * maze_width) + 1
        expanded_height = (2 * maze_height) + 1

        all_walls_mask = self.mask_north | self.mask_south | self.mask_east | self.mask_west

        if self.visited is not None:
            display_grid = [[Symbols.EMPTY for _ in range(expanded_width)]
                            for _ in range(expanded_height)]

            for y, row in enumerate(self.grid):
                for x, logical_cell in enumerate(row):
                    if (x, y) not in self.visited:
                        continue

                    center_y, center_x = (y * 2) + 1, (x * 2) + 1
                    current_coord = (x, y)

                    if current_coord in self.pattern_42_cells:
                        char_42 = f"{Colors.NUMBER_42}{Symbols.WALL_BLOCK}{Colors.RESET}"

                        for dy in [-1, 0, 1]:
                            for dx in [-1, 0, 1]:
                                display_grid[center_y + dy][center_x + dx] = char_42
                        continue

                    display_grid[center_y][center_x] = self._get_cell_visual(
                        (x, y))

                    if self._has_wall(logical_cell, self.mask_north):
                        display_grid[center_y - 1][center_x] = wall_char
                    if self._has_wall(logical_cell, self.mask_south):
                        display_grid[center_y + 1][center_x] = wall_char
                    if self._has_wall(logical_cell, self.mask_east):
                        display_grid[center_y][center_x + 1] = wall_char
                    if self._has_wall(logical_cell, self.mask_west):
                        display_grid[center_y][center_x - 1] = wall_char

                    display_grid[center_y - 1][center_x - 1] = wall_char
                    display_grid[center_y - 1][center_x + 1] = wall_char
                    display_grid[center_y + 1][center_x - 1] = wall_char
                    display_grid[center_y + 1][center_x + 1] = wall_char
        else:
            display_grid = self._create_blank_expanded_grid(wall_char)

            for y, row in enumerate(self.grid):
                for x, logical_cell in enumerate(row):

                    center_y, center_x = (y * 2) + 1, (x * 2) + 1
                    current_coord = (x, y)
                    visual = self._get_cell_visual(current_coord)

                    if current_coord in self.pattern_42_cells:
                        char_42 = f"{Colors.NUMBER_42}{Symbols.WALL_BLOCK}{Colors.RESET}"

                        for dy in [-1, 0, 1]:
                            for dx in [-1, 0, 1]:
                                display_grid[center_y + dy][center_x + dx] = char_42
                        continue

                    if visual == Symbols.EMPTY and logical_cell == all_walls_mask:
                        pass
                    else:
                        display_grid[center_y][center_x] = self._get_cell_visual(
                            current_coord)

                    if not self._has_wall(logical_cell, self.mask_east):
                        display_grid[center_y][center_x + 1] = Symbols.EMPTY

                    if not self._has_wall(logical_cell, self.mask_south):
                        display_grid[center_y + 1][center_x] = Symbols.EMPTY

        for row in display_grid:
            print("".join(row))
