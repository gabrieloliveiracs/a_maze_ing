import time
from config import Config
from solver import MazeSolver
from ascii_renderer import ASCIIRenderer, Colors
from mazegen import MazeGenerator


class MazeController:
    def __init__(self, renderer: ASCIIRenderer, config: Config) -> None:
        self.renderer = renderer
        self.config = config

    def _clear_screen(self) -> None:
        print("\033[2J\033[H", end="")

    def process_maze(self, maze: MazeGenerator) -> None:
        self.renderer.grid = maze.grid

        self._clear_screen()
        print("\033[?25l", end="", flush=True)
        try:
            for pos in maze.carve_path():
                self.renderer.visited = maze.visited
                self.renderer.current_cell = pos
                self.renderer.stack = maze.stack
                print("\033[H\n", end="")
                self.renderer.render()
                time.sleep(0.03)
        finally:
            print("\033[?25h", end="", flush=True)

        self.renderer.visited = None
        self.renderer.current_cell = None
        self.renderer.stack = None

        solver = MazeSolver(maze)
        solver.dead_end_fill(maze)

        if hasattr(solver, 'path'):
            self.renderer.path = solver.path

    def run(self, initial_maze: MazeGenerator) -> None:
        self.process_maze(initial_maze)
        try:
            while True:
                self._clear_screen()
                print("\n")
                self.renderer.render()

                print(f"\n{Colors.BOLD}--- Menu Interativo ---{Colors.RESET}")
                print("[1] Gerar novo mapa")
                print(
                    f"[2] {'Esconder' if self.renderer.show_path else 'Mostrar'} caminho")
                print("[3] Mudar cor das paredes")
                print("[4] Sair")

                try:
                    user_choice = int(input("\nEscolha uma opção de 1 a 4: "))

                    if user_choice == 1:
                        new_maze = MazeGenerator(
                            self.config.width, self.config.height, self.config.entry)
                        self.process_maze(new_maze)

                    elif user_choice == 2:
                        self.renderer.show_path = not self.renderer.show_path

                    elif user_choice == 3:
                        self.renderer.color_idx = (
                            self.renderer.color_idx + 1) % len(Colors.WALLS)

                    elif user_choice == 4:
                        print("\nEncerrando...")
                        break

                    else:
                        print("\nDigite um número de 1 a 4!")
                        input("Pressione ENTER para continuar...")

                except ValueError:
                    print("\nDigite somente opções válidas (números inteiros)!")
                    input("Pressione ENTER para continuar...")

        except KeyboardInterrupt:
            # handle Ctrl+C exit and restore cursor
            print("\033[?25h\n\nSaindo...")
