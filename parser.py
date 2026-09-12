# parser.py
from typing import Tuple
from mazegen.config import Config

def parse_config(file_path: str) -> Config:
    width = height = None
    entry = exit_point = None
    output_file = None
    perfect = None

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
                    perfect = val.lower() == 'true'
                else:
                    raise KeyError(key)
            except KeyError as error:
                raise ValueError(
                    f"Chave desconhecida no arquivo config: {error.args[0]}"
                ) from error
            except ValueError as error:
                raise ValueError(
                    f"Valor inválido na linha config: {line}"
                ) from error

    if (width is None or height is None or entry is None or exit_point is None
            or output_file is None or perfect is None):
        raise ValueError(
            "Config deve definir WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE e PERFECT"
        )

    return Config(
        width=width,
        height=height,
        entry=entry,
        exit=exit_point,
        output_file=output_file,
        perfect=perfect,
    )