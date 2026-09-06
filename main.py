from typing import List, Tuple
from ascii_renderer import ASCIIRenderer

def save_maze(grid: List[List[int]], entry: Tuple[int, int],
            exit_point: Tuple[int, int], path: List[Tuple[int, int]],
            file_name: str) -> None:
    with open(file_name, "w") as arquivo:
        for linha in grid:
            for brick in linha:
                arquivo.write(f"{brick:X}")
            arquivo.write("\n")

        arquivo.write("\n")
        arquivo.write(f"{entry[0]},{entry[1]}\n")
        arquivo.write(f"{exit_point[0]},{exit_point[1]}\n")


        string_caminho = ""
        for i in range(len(path) - 1):
            passo_atual = path[i]
            proximo_passo = path[i + 1]
            if passo_atual[0] < proximo_passo[0]:
                string_caminho += "E"
            elif passo_atual[0] > proximo_passo[0]:
                string_caminho += "W"
            elif passo_atual[1] < proximo_passo[1]:
                string_caminho += "S"
            elif passo_atual[1] > proximo_passo[1]:
                string_caminho += "N"

        arquivo.write(string_caminho + "\n")

def main() -> None:
    """Simulando MazeGenerator"""
    fake_grid = [
        [9, 5, 3, 15, 10],
        [10, 15, 10, 0, 10],
        [9, 5, 3, 15, 10],
        [12, 5, 14, 15, 6],
    ]
    fake_entry = (1, 1)
    fake_exit = (3, 3)
    fake_path = [(1, 1),(2, 1), (3, 1), (3, 2), (3, 3)]
    output_file = "output_maze.txt"
    """Simulando arquivo de saída"""
    save_maze(fake_grid, fake_entry, fake_exit, fake_path, output_file)
    """Renderização"""
    print("\nIniciando...")
    resultado = ASCIIRenderer(fake_grid, fake_entry, fake_exit, fake_path)
    resultado.interactive_menu()

if __name__ == "__main__":
    main()
