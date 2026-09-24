import sys
from typing import List, Tuple
from ascii_renderer import ASCIIRenderer
from config import Config
from mazegen import MazeGenerator
from solver import MazeSolver
from controller import MazeController


def main() -> None:
    config_path = sys.argv[1]
    print(config_path)

    config = Config.from_file(config_path)
    print(f"Configuração carregada: {config}")

    maze = MazeGenerator(config.width, config.height, config.entry)
    maze.carve_path()
    solver = MazeSolver(maze)
    print(maze.grid)
    solver.dead_end_fill(maze)
    resultado = ASCIIRenderer(
        grid=maze.grid,
        entry=config.entry,
        exit_point=config.exit,
        path=[],
        config=config
    )

    controller = MazeController(resultado, config)
    controller.run()


if __name__ == "__main__":
    main()
