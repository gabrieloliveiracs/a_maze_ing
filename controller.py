import os
from config import Config
from ascii_renderer import ASCIIRenderer, Colors
from mazegen import MazeGenerator

class MazeController:
    def __init__(self, renderer: ASCIIRenderer, config: Config) -> None:
        self.renderer = renderer
        self.config = config

    def run(self) -> None:
        while True:
            os.system('clear')
            print("\n")
            self.renderer.render()

            print(f"\n{Colors.BOLD}--- Menu Interativo ---{Colors.RESET}")
            print("[1] Gerar novo mapa")
            print(f"[2] {'Esconder' if self.renderer.show_path else 'Mostrar'} caminho")
            print("[3] Mudar cor das paredes")
            print("[4] Sair")

            try:
                user_choice = int(input("\nEscolha uma opção de 1 a 4: "))

                if user_choice == 1:
                    new_maze = MazeGenerator(self.config)
                    new_maze.carve_path()
                    self.renderer.grid = new_maze.grid
                elif user_choice == 2:
                    self.renderer.show_path = not self.renderer.show_path
                elif user_choice == 3:
                    self.renderer.color_idx = (self.renderer.color_idx + 1) % len(Colors.WALLS)
                elif user_choice == 4:
                    print("\nEncerrando...")
                    break
                else:
                    print("\nDigite um número de 1 a 4!")
                    input("Pressione ENTER para continuar...")

            except ValueError:
                print("\nDigite somente opções válidas (números inteiros)!")
                input("Pressione ENTER para continuar...")
