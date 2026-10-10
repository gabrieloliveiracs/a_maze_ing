#!/usr/bin/env python3
import sys
from config import Config
from mazegen import MazeGenerator
from ascii_renderer import ASCIIRenderer
from controller import MazeController


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    config_path = sys.argv[1]

    try:
        config = Config.from_file(config_path)
    except OSError as error:
        print(
            f"Configuration error: cannot read '{config_path}': "
            f"{error}")
        sys.exit(1)
    except ValueError as error:
        print(f"Configuration error: {error}")
        sys.exit(1)

    try:
        maze = MazeGenerator(config.width, config.height,
                             config.entry, config.exit, config.seed)
    except ValueError as error:
        print(f"Maze configuration error: {error}")
        sys.exit(1)
    except Exception as error:
        print(f"Maze generation failed: {error}")
        sys.exit(1)

    renderer = ASCIIRenderer(
        grid=maze.grid,
        entry=config.entry,
        exit_point=config.exit,
        path=[],
        config=config
    )
    controller = MazeController(renderer, config)
    try:
        controller.run(maze)
    except Exception as error:
        print(f"Maze processing failed: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
