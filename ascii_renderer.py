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
        self.stack = None

        self.pattern_42_cells = set()
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
        is_animated = self.visited is not None
        wall_char = self._get_wall_character()

        display_grid = self._initialize_display_grid()

        for maze_y, row in enumerate(self.grid):
            for maze_x, cell_walls in enumerate(row):
                coord = (maze_x, maze_y)

                if is_animated and coord not in self.visited:
                    continue

                display_x, display_y = self._get_display_coordinates(
                    maze_x, maze_y)

                self._draw_cell(display_grid, display_x, display_y,
                                cell_walls, coord, wall_char)

        self._apply_pattern_42(display_grid)
        self._print_grid(display_grid)

    def _get_wall_character(self) -> str:
        wall_color = Colors.WALLS[self.color_idx]
        return f"{wall_color}{Symbols.WALL_BLOCK}{Colors.RESET}"

    def _get_display_dimensions(self) -> Tuple[int, int]:
        maze_height = len(self.grid)
        maze_width = len(self.grid[0])

        expanded_width = (2 * maze_width) + 1
        expanded_height = (2 * maze_height) + 1

        return expanded_width, expanded_height

    def _initialize_display_grid(self) -> List[List[str]]:
        width, height = self._get_display_dimensions()
        return [[Symbols.EMPTY for _ in range(width)] for _ in range(height)]

    def _get_display_coordinates(self, maze_x: int, maze_y: int) -> Tuple[int, int]:
        return (maze_x * 2) + 1, (maze_y * 2) + 1

    def _draw_cell(self, grid: List[List[str]], cx: int, cy: int, logical_cell: int, coord: Coordinate, wall_char: str) -> None:
        all_walls = self.mask_north | self.mask_south | self.mask_east | self.mask_west
        visual = self._get_cell_visual(coord)

        if visual == Symbols.EMPTY and logical_cell == all_walls:
            grid[cy][cx] = wall_char
        else:
            grid[cy][cx] = visual

        if self._has_wall(logical_cell, self.mask_north):
            grid[cy - 1][cx] = wall_char
        if self._has_wall(logical_cell, self.mask_south):
            grid[cy + 1][cx] = wall_char
        if self._has_wall(logical_cell, self.mask_east):
            grid[cy][cx + 1] = wall_char
        if self._has_wall(logical_cell, self.mask_west):
            grid[cy][cx - 1] = wall_char

        grid[cy - 1][cx - 1] = grid[cy - 1][cx + 1] = wall_char
        grid[cy + 1][cx - 1] = grid[cy + 1][cx + 1] = wall_char

    def _apply_pattern_42(self, grid: List[List[str]]) -> None:
        char_42 = f"{Colors.NUMBER_42}{Symbols.WALL_BLOCK}{Colors.RESET}"

        for maze_x, maze_y in self.pattern_42_cells:
            center_x, center_y = self._get_display_coordinates(maze_x, maze_y)

            for row_offset in [-1, 0, 1]:
                for col_offset in [-1, 0, 1]:
                    target_y = center_y + row_offset
                    target_x = center_x + col_offset

                    if self._is_within_bounds(grid, target_x, target_y):
                        grid[target_y][target_x] = char_42

    def _is_within_bounds(self, grid: List[List[str]], x: int, y: int) -> bool:
        return 0 <= y < len(grid) and 0 <= x < len(grid[0])

    def _print_grid(self, grid: List[List[str]]) -> None:
        for row in grid:
            print("".join(row))
