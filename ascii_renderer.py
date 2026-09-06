from typing import List, Tuple

class ASCIIRenderer:
    def __init__(self, grid: List[List[int]], entry: Tuple[int, int],
                exit_point: Tuple[int, int], path: List[Tuple[int, int]]) -> None:
        self.grid = grid
        self.entry = entry
        self.exit_point = exit_point
        self.path = path
        self.show_path = True

    def compass(self, brick: int) -> List[str]:
        paredes = []
        if brick & 1: paredes.append("N")
        if brick & 2: paredes.append("E")
        if brick & 4: paredes.append("S")
        if brick & 8: paredes.append("W")
        return paredes

    def render(self) -> None:
        """Desenhando matriz com unicode!"""
        mapa_caracteres = {
            0: " ", 1: "╵", 2: "╶", 3: "└", 
            4: "╷", 5: "│", 6: "┌", 7: "├",
            8: "╴", 9: "┘", 10: "─", 11: "┴", 
            12: "┐", 13: "┤", 14: "┬", 15: "┼"
        }

        for y, linha in enumerate(self.grid):
            for x, brick in enumerate(linha):
                coordenada = (x, y)
                if coordenada == self.entry:
                    print("S", end="")
                elif coordenada == self.exit_point:
                    print("E", end="")
                elif coordenada in self.path and self.show_path:
                    print(".", end="")
                else:
                    print(mapa_caracteres.get(brick, " "), end="")
                    #print("#", end="") Unicode ficou ruim, usar esse para ver melhor.
            print()

    def interactive_menu(self):
        while True:
            print("\n")
            self.render()

            print("\n--- Menu interative ---")
            print("[1] Gerar novo mapa")
            print("[2] Mostrar/esconder caminho")
            print("[3] Mudar cor (esperar interface gráfica)")
            print("[4] Sair")

            try:
                resposta = int(input("\nEscolha uma opção de 1 a 4: "))
                if resposta == 1:
                    print("\nEsperar MazeGenerator...")
                elif resposta == 2:
                    self.show_path = not self.show_path
                elif resposta == 3:
                    print("\nAguardar interface gráfica...")
                elif resposta == 4:
                    print("\nEncerrando...")
                    break
                else:
                    print("\nDigite um número de 1 a 4!")
            except ValueError:
                print("\nDigite somente as opção válidas!")
