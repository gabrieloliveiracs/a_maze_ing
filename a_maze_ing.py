#!/usr/bin/env python3
import sys
from config import Config
from mazegen import MazeGenerator
from solver import MazeSolver
from ascii_renderer import ASCIIRenderer
from controller import MazeController


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    config_path = sys.argv[1]

    config = Config.from_file(config_path)
    maze = MazeGenerator(config.width, config.height,
                         config.entry, config.exit, config.seed)
    renderer = ASCIIRenderer(
        grid=maze.grid,
        entry=config.entry,
        exit_point=config.exit,
        path=[],
        config=config
    )
    controller = MazeController(renderer, config)
    controller.run(maze)


if __name__ == "__main__":
    main()
