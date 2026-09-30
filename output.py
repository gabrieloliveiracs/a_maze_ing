from typing import List, Tuple

class MazeOutput:
    def __init__(self, grid: List[List[int]], entry: Tuple[int, int],
                 exit_point: Tuple[int, int], path: List[Tuple[int, int]]) -> None:
        self.grid = grid
        self.entry = entry
        self.exit_point = exit_point
        self.path = path

    def save_maze(self, file_name: str) -> None:
        with open(file_name, "w") as file:
                
            for line in self.grid:
                for brick in line:
                    file.write(f"{brick:X}")
                file.write("\n")

            file.write("\n")
            file.write(f"{self.entry[0]}, {self.entry[1]}\n")
            file.write(f"{self.exit_point[0]}, {self.exit_point[1]}\n")

            string_path = ""

            for i in range(len(self.path) - 1):
                current, next = self.path[i], self.path[i + 1]
                if current[0] < next[0]: string_path += "E"
                elif current[0] > next[0]: string_path += "W"
                elif current[1] < next[1]: string_path += "S"
                elif current[1] > next[1]: string_path += "N"
                
            file.write(string_path + "\n")
