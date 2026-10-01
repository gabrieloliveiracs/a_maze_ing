import time
from simple_term_menu import TerminalMenu
from config import Config
from solver import MazeSolver
from ascii_renderer import ASCIIRenderer, Colors
from mazegen import MazeGenerator
from output import MazeOutput


class MazeController:
    def __init__(self, renderer: ASCIIRenderer, config: Config) -> None:
        self.renderer = renderer
        self.config = config
        self.generation_algorithm = "prim"
        self.animation_speed = "auto"
        self.animation_speed_options = ("auto", "slow", "normal", "fast")

    def _clear_screen(self) -> None:
        print("\033[2J\033[3J\033[H", end="")

    def _hide_cursor(self) -> None:
        print("\033[?25l", end="", flush=True)

    def _show_cursor(self) -> None:
        print("\033[?25h", end="", flush=True)

    def _move_cursor_top(self) -> None:
        print("\033[H\n", end="")

    def _get_animation_delay(self, maze: MazeGenerator) -> float:
        preset_delays = {"slow": 0.04, "normal": 0.012, "fast": 0.003}
        if self.animation_speed != "auto":
            return preset_delays[self.animation_speed]

        estimated_frames = max(1, maze.width * maze.height)
        if self.generation_algorithm == "dfs":
            estimated_frames *= 2

        return min(0.04, 3.0 / estimated_frames)

    def process_maze(self, maze: MazeGenerator) -> None:
        self.renderer.grid = maze.grid
        self.renderer.pattern_42_cells = maze.pattern_42_cells
        self.renderer.path = []

        solver = MazeSolver(maze)
        self._animate_generation(maze, solver)
        self._reset_animation_state()
        self._solve_and_attach_path(solver)

        exportador = MazeOutput(maze.grid, self.config.entry, self.config.exit,
                                self.renderer.path)
        exportador.save_maze(self.config.output_file)

    def _animate_generation(self, maze: MazeGenerator, solver: MazeSolver) -> None:
        self._clear_screen()
        self._hide_cursor()
        try:
            animation_delay = self._get_animation_delay(maze)
            generate = (
                maze.prim_path
                if self.generation_algorithm == "prim"
                else maze.carve_path
            )
            for current_position in generate():
                self.renderer.visited = maze.visited
                self.renderer.current_cell = current_position
                self.renderer.stack = maze.stack

                self._move_cursor_top()
                self.renderer.render()
                time.sleep(animation_delay)

            if not self.config.perfect:
                for current_position in maze.braid():
                    self.renderer.current_cell = current_position
                    self._move_cursor_top()
                    self.renderer.render()
                    time.sleep(animation_delay)

            self._reset_animation_state()
            for current_position in solver.dead_end_fill():
                self.renderer.current_cell = current_position

                self._move_cursor_top()
                self.renderer.render()
                time.sleep(animation_delay)
        finally:
            self._show_cursor()

    def _reset_animation_state(self) -> None:
        self.renderer.visited = None
        self.renderer.current_cell = None
        self.renderer.stack = None

    def _solve_and_attach_path(self, solver: MazeSolver) -> None:
        self.renderer.path = solver.path

    def run(self, initial_maze: MazeGenerator) -> None:
        self.process_maze(initial_maze)

        try:
            while True:
                self._clear_screen()
                print("\n")
                self.renderer.render()
                print(f"\n{Colors.BOLD}--- Maze Menu ---{Colors.RESET}")

                algorithm_name = (
                    "Prim" if self.generation_algorithm == "prim"
                    else "Recursive Backtracker"
                )
                next_algorithm_name = (
                    "Recursive Backtracker" if self.generation_algorithm == "prim"
                    else "Prim"
                )
                animation_speed_name = {
                    "auto": "Auto (map-adaptive)",
                    "slow": "Slow",
                    "normal": "Normal",
                    "fast": "Fast",
                }[self.animation_speed]

                menu_options = [
                    "Generate new map",
                    "Hide path" if self.renderer.show_path else "Show path",
                    f"Generation algorithm: {algorithm_name} (switch to {next_algorithm_name})",
                    f"Animation speed: {animation_speed_name}",
                    "Change wall color",
                    "Exit",
                ]
                user_choice = TerminalMenu(
                    menu_options,
                    menu_cursor="> ",
                    menu_cursor_style=("fg_yellow", "bold"),
                    menu_highlight_style=("fg_cyan", "bold"),
                    status_bar="Arrow keys: move | Enter: select",
                    cycle_cursor=True,
                ).show()

                if user_choice is None or user_choice == 5:
                    print("\nExiting...")
                    break
                if user_choice == 0:
                    new_maze = MazeGenerator(
                        self.config.width,
                        self.config.height,
                        self.config.entry,
                        self.config.exit,
                        self.config.seed,
                    )
                    self.process_maze(new_maze)
                elif user_choice == 1:
                    self.renderer.show_path = not self.renderer.show_path
                elif user_choice == 2:
                    self.generation_algorithm = (
                        "dfs" if self.generation_algorithm == "prim" else "prim"
                    )
                elif user_choice == 3:
                    current_speed_index = self.animation_speed_options.index(
                        self.animation_speed
                    )
                    next_speed_index = (
                        current_speed_index + 1
                    ) % len(self.animation_speed_options)
                    self.animation_speed = self.animation_speed_options[next_speed_index]
                elif user_choice == 4:
                    self.renderer.color_idx = (
                        self.renderer.color_idx + 1) % len(Colors.WALLS)

        except KeyboardInterrupt:
            self._show_cursor()
            print("\n\nExiting...")
