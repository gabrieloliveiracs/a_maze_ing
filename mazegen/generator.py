from config import Config
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

    def carve_path():
        