from mazegen import MazeGenerator


class MazeSolver:
    def __init__(self, maze: MazeGenerator, algorithm="dead-end-fill"):
        self.maze = maze.grid
        self.path = []
        self.entry = maze.entry

    def _is_dead_end(self, x, y) -> int:
        return self.maze[x][y].bit_count() >= 3

    def dead_end_fill(self, maze):
        for row in range(len(self.maze)):
            for col in range(len(self.maze[0])):
                if self._is_dead_end(row, col):
                    # "paint"
                    print(self.maze[row][col])
                    ...
        ...
