from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Config:
    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str
    perfect: bool = False
    seed: Optional[int] = None

    def __post_init__(self) -> None:
        if self.width < 1 or self.height < 1:
            raise ValueError("Maze dimensions must be positive")
        if len(self.entry) != 2 or len(self.exit) != 2:
            raise ValueError("Entry and exit must each contain x,y coordinates")
        if self.entry == self.exit:
            raise ValueError("Entry and exit must be different cells")
        for name, (x, y) in (("Entry", self.entry), ("Exit", self.exit)):
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise ValueError(f"{name} must be inside the maze bounds")

    @classmethod
    def from_file(cls, file_path: str) -> "Config":
        width = height = None
        entry = exit_point = None
        output_file = None
        perfect = False
        seed = None

        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                try:
                    key, val = line.split('=', 1)
                    if key == 'WIDTH':
                        width = int(val)
                    elif key == 'HEIGHT':
                        height = int(val)
                    elif key == 'ENTRY':
                        entry = tuple(map(int, val.split(',')))
                    elif key == 'EXIT':
                        exit_point = tuple(map(int, val.split(',')))
                    elif key == 'OUTPUT_FILE':
                        output_file = val
                    elif key == 'PERFECT':
                        normalized = val.lower()
                        if normalized not in ('true', 'false'):
                            raise ValueError("PERFECT must be true or false")
                        perfect = normalized == 'true'
                    elif key == 'SEED':
                        seed = int(val)
                    else:
                        raise KeyError(key)
                except KeyError as error:
                    raise ValueError(
                        f"Unknown config key: {error.args[0]}"
                    ) from error
                except ValueError as error:
                    raise ValueError(
                        f"Invalid value on config line: {line}"
                    ) from error

        if (width is None or height is None or entry is None or exit_point is None
            or output_file is None):
            raise ValueError(
            "Config must define WIDTH, HEIGHT, ENTRY, EXIT, and OUTPUT_FILE"
            )

        return cls(
            width=width,
            height=height,
            entry=entry,
            exit=exit_point,
            output_file=output_file,
            perfect=perfect,
            seed=seed,
        )
