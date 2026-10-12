from dataclasses import dataclass
from typing import Iterable, Optional, Tuple, cast
import re

REQUIRED_KEYS = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE")
KNOWN_KEYS = set(REQUIRED_KEYS) | {"PERFECT", "SEED"}


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
            raise ValueError(
                "Entry and exit must each contain x,y coordinates"
            )
        if self.entry == self.exit:
            raise ValueError("Entry and exit must be different cells")
        for name, coordinates in (
            ("Entry", self.entry),
            ("Exit", self.exit),
        ):
            x, y = coordinates
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise ValueError(f"{name} must be inside the maze bounds")

    @classmethod
    def from_file(cls, file_path: str) -> "Config":
        try:
            with open(file_path, "r") as config_file:
                values = cls._parse_lines(config_file)
        except FileNotFoundError:
            raise ValueError(
                f"Configuration file '{file_path}' was not found"
            )
        except PermissionError:
            raise ValueError(
                f"Configuration file '{file_path}' cannot be read: permission"
                f"denied"
            )
        except OSError as error:
            raise ValueError(
                f"Configuration file '{file_path}' cannot be read: {error}"
            )

        missing = [key for key in REQUIRED_KEYS if key not in values]
        if missing:
            raise ValueError(
                "Configuration is missing required key(s): "
                + ', '.join(missing)
            )

        return cls(
            width=cast(int, values["WIDTH"]),
            height=cast(int, values["HEIGHT"]),
            entry=cast(Tuple[int, int], values["ENTRY"]),
            exit=cast(Tuple[int, int], values["EXIT"]),
            output_file=cast(str, values["OUTPUT_FILE"]),
            perfect=cast(bool, values.get("PERFECT", False)),
            seed=cast(Optional[int], values.get("SEED")),
        )

    @classmethod
    def _parse_lines(cls, lines: Iterable[str]) -> dict[str, object]:
        values: dict[str, object] = {}

        for line_number, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            key, value = cls._split_line(line, line_number)
            if key in values:
                raise ValueError(
                    f"Configuration line {line_number} repeats key '{key}'"
                )
            if key not in KNOWN_KEYS:
                raise ValueError(
                    f"Configuration line {line_number} uses unknown key "
                    f"'{key}'"
                )
            if not value:
                raise ValueError(
                    f"Configuration key '{key}' on line {line_number} "
                    "must have a value"
                )

            try:
                values[key] = cls._parse_value(key, value)
            except ValueError as error:
                raise ValueError(
                    f"Invalid value for '{key}' on line {line_number} "
                    f"('{value}'): {error}"
                ) from error

        return values

    @staticmethod
    def _split_line(line: str, line_number: int) -> Tuple[str, str]:
        if "=" not in line:
            raise ValueError(
                f"Configuration line {line_number} is malformed: "
                f"expected KEY=VALUE, got '{line}'"
            )

        key, value = (part.strip() for part in line.split("=", 1))
        if not key:
            raise ValueError(
                f"Configuration line {line_number} has an empty key"
            )
        return key, value

    @staticmethod
    def _parse_value(key: str, value: str) -> object:
        if key in ("WIDTH", "HEIGHT", "SEED"):
            return int(value)
        if key in ("ENTRY", "EXIT"):
            coordinates = [int(part.strip()) for part in value.split(",")]
            if len(coordinates) != 2:
                raise ValueError("expected exactly two coordinates")
            return coordinates[0], coordinates[1]
        if key == "OUTPUT_FILE":
            pattern = re.compile(r"^.+\.txt$")
            if not pattern.match(value):
                raise ValueError("output file needs to have valid .txt format")
            return value
        if key == "PERFECT":
            normalized = value.lower()
            if normalized not in ("true", "false"):
                raise ValueError("expected 'true' or 'false'")
            return normalized == "true"
        raise ValueError(f"unsupported configuration key '{key}'")
