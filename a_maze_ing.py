#!/usr/bin/env python3
import sys
import os
import time
from ascii_renderer import ASCIIRenderer, Colors
from config import Config
from mazegen import MazeGenerator
from solver import MazeSolver
from controller import MazeController


def main() -> None:
    config_path = sys.argv[1]

    config = Config.from_file(config_path)

    maze = MazeGenerator(config.width, config.height, config.entry)
    resultado = ASCIIRenderer(
        grid=maze.grid,
        entry=config.entry,
        exit_point=config.exit,
        path=[],
        config=config
    )

    solver = MazeSolver(maze)
    solver.dead_end_fill(maze)

    controller = MazeController(resultado, config)
    controller.run(maze)


if __name__ == "__main__":
    main()
