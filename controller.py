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

    def _hide_cursor(self) -> None:
        print("\033[?25l", end="", flush=True)

    def _show_cursor(self) -> None:
        print("\033[?25h", end="", flush=True)

    def _move_cursor_top(self) -> None:
        print("\033[H\n", end="")

    def process_maze(self, maze: MazeGenerator) -> None:
        self.renderer.grid = maze.grid

        self._animate_generation(maze)
        self._reset_animation_state()
        self._solve_and_attach_path(maze)

    def _animate_generation(self, maze: MazeGenerator) -> None:
        self._clear_screen()
        self._hide_cursor()

        try:
            for current_position in maze.carve_path():
                self.renderer.visited = maze.visited
                self.renderer.current_cell = current_position
                self.renderer.stack = maze.stack

                self._move_cursor_top()
                self.renderer.render()
                time.sleep(0.03)
        finally:
            self._show_cursor()

    def _reset_animation_state(self) -> None:
        self.renderer.visited = None
        self.renderer.current_cell = None
        self.renderer.stack = None

    def _solve_and_attach_path(self, maze: MazeGenerator) -> None:
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
            self._show_cursor()
            print("\n\nSaindo...")
