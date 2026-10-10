from typing import List, Tuple

MazeGrid = List[List[int]]


class MazeDisplay:
    """Motor Gráfico para MLX"""

    def __init__(
        self,
        grid: List[List[int]],
        screen_width: int,
        screen_height: int,
    ) -> None:
        self.grid: MazeGrid = grid
        self.width = screen_width
        self.height = screen_height
        self.bytes_pixel = 4
        self.stride = self.width * self.bytes_pixel
        self.image_buffer = bytearray(self.height * self.stride)
        self.brick_size = 20

    def pixel_color(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            pass
