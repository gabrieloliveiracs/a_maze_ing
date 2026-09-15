import os
from typing import List, Tuple

from constants import DIRECTION_OFFSETS
from mazegen import MazeGenerator, MazeSolver
from mazegen import Config

Coordinate = Tuple[int, int]
MazeGrid = List[List[int]]


class Colors:
    """
    Códigos ANSI usados para formatar e colorir texto no terminal.
    Sintaxe base: \\033[<código>m
    """
    # --- Estilos ---
    RESET = '\033[0m'  # 0: Remove todas as formatações (restaura a cor padrão)
    BOLD = '\033[1m'   # 1: Deixa o texto em negrito

    # --- Elementos do Jogo (Fundo + Texto) ---
    # Família 40 = Cores de Fundo (Background) | Família 30 = Cores de Texto (Foreground)
    START = '\033[42m\033[30m'  # 42: Fundo Verde    | 30: Texto Preto
    END = '\033[41m\033[30m'    # 41: Fundo Vermelho | 30: Texto Preto
    PATH = '\033[43m\033[30m'   # 43: Fundo Amarelo  | 30: Texto Preto

    # --- Opções de Cores das Paredes ---
    # Família 30 = Cores Normais | Família 90 = Cores Brilhantes (High-intensity)
    WALLS = [
        '\033[36m',  # 36: Ciano (Azul claro padrão)
        '\033[94m',  # 94: Azul Brilhante
        '\033[95m',  # 95: Magenta Brilhante (Rosa/Roxo)
        '\033[37m',  # 37: Branco / Cinza Claro
        '\033[32m'   # 32: Verde
    ]


class Symbols:
    """Caracteres usados para desenhar os elementos do labirinto."""
    WALL_BLOCK = "██"
    EMPTY = "  "
    START_POINT = f"{Colors.START}SS{Colors.RESET}"
    EXIT_POINT = f"{Colors.START}EE{Colors.RESET}"
    PATH_TRAIL = f"{Colors.START}..{Colors.RESET}"


class ASCIIRenderer:
    """Renderizador ASCII interativo para visualização de labirintos."""

    def __init__(
        self,
        grid: MazeGrid,
        entry: Coordinate,
        exit_point: Coordinate,
        path: List[Coordinate],
        config: Config
    ) -> None:
        self.grid = grid
        self.entry = entry
        self.exit_point = exit_point
        self.path = path
        self.config = config
        self.show_path = True
        self.color_idx = 0

        # Máscaras de bits para identificar onde há paredes lógicas
        self.mask_north = 0
        self.mask_south = 0
        self.mask_east = 0
        self.mask_west = 0
        self._map_directional_masks()

    def _map_directional_masks(self) -> None:
        """Decifra qual número (bit) representa cada direção com base nos eixos X e Y."""
        for wall_mask, (dx, dy) in DIRECTION_OFFSETS.items():
            if dy < 0:
                self.mask_north = wall_mask
            elif dy > 0:
                self.mask_south = wall_mask
            elif dx > 0:
                self.mask_east = wall_mask
            elif dx < 0:
                self.mask_west = wall_mask

    def _has_wall(self, cell_value: int, direction_mask: int) -> bool:
        """Retorna True se a célula possui uma parede na direção especificada (Bitwise AND)."""
        return bool(cell_value & direction_mask)

    def _create_blank_expanded_grid(self, wall_char: str) -> List[List[str]]:
        """
        Cria a matriz expandida inicial, preenchida inteiramente por paredes.
        Fórmula: (Salas * 2) + 1 parede final para fechar a borda.
        """
        maze_height, maze_width = len(self.grid), len(self.grid[0])
        expanded_width = (2 * maze_width) + 1
        expanded_height = (2 * maze_height) + 1

        return [[wall_char for _ in range(expanded_width)] for _ in range(expanded_height)]

    def _get_cell_visual(self, coord: Coordinate) -> str:
        """Determina qual visualização de 'chão' deve ser desenhada para uma coordenada."""
        if coord == self.entry:
            return Symbols.START_POINT
        if coord == self.exit_point:
            return Symbols.EXIT_POINT
        if coord in self.path and self.show_path:
            return Symbols.PATH_TRAIL

        return Symbols.EMPTY

    def render(self) -> None:
        """Constrói e imprime o labirinto renderizado no terminal."""
        current_wall_color = Colors.WALLS[self.color_idx]
        wall_char = f"{current_wall_color}{Symbols.WALL_BLOCK}{Colors.RESET}"

        # 1. Começamos com um bloco sólido de paredes
        display_grid = self._create_blank_expanded_grid(wall_char)

        # 2. Esculpimos as salas e os caminhos
        for y, row in enumerate(self.grid):
            for x, logical_cell in enumerate(row):

                # Mapeia a coordenada lógica (x, y) para o centro da sala na matriz expandida (ímpares)
                center_y, center_x = (y * 2) + 1, (x * 2) + 1
                current_coord = (x, y)

                # Esculpe o chão da sala atual
                display_grid[center_y][center_x] = self._get_cell_visual(
                    current_coord)

                # Abre buracos nas paredes conectando as salas (se não houver parede lógica)
                if not self._has_wall(logical_cell, self.mask_east):
                    display_grid[center_y][center_x + 1] = Symbols.EMPTY

                if not self._has_wall(logical_cell, self.mask_south):
                    display_grid[center_y + 1][center_x] = Symbols.EMPTY

        # 3. Imprime o resultado final
        for row in display_grid:
            print("".join(row))

    def interactive_menu(self) -> None:
        """Loop principal de interação do usuário."""
        while True:
            os.system('clear')
            print("\n")
            self.render()

            print(f"\n{Colors.BOLD}--- Menu Interativo ---{Colors.RESET}")
            print("[1] Gerar novo mapa")
            print(f"[2] {'Esconder' if self.show_path else 'Mostrar'} caminho")
            print("[3] Mudar cor das paredes")
            print("[4] Sair")

            try:
                user_choice = int(input("\nEscolha uma opção de 1 a 4: "))

                if user_choice == 1:
                    new_maze = MazeGenerator(self.config)
                    new_maze.carve_path()
                    self.grid = new_maze.grid
                elif user_choice == 2:
                    self.show_path = not self.show_path
                elif user_choice == 3:
                    self.color_idx = (self.color_idx + 1) % len(Colors.WALLS)
                elif user_choice == 4:
                    print("\nEncerrando...")
                    break
                else:
                    print("\nDigite um número de 1 a 4!")
                    input("Pressione ENTER para continuar...")

            except ValueError:
                print("\nDigite somente opções válidas (números inteiros)!")
                input("Pressione ENTER para continuar...")
    # North = 1  (Binary: 0001)
    # South = 2  (Binary: 0010)
    # East  = 4  (Binary: 0100)
    # West  = 8  (Binary: 1000)
    #     1001  (The cell value: 9)
    # &   1000  (The mask for West: 8)
    # ------
    #     1000  (The result: 8)
#   _________________________________
    #     1001  (The cell value: 9)
    # &   0100  (The mask for East: 4)
    #   ------
    #     0000  (The result: 0)
