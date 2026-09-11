import sys
from config import Config

def parse_config(config_path):
    raw_data = {}

    try:
        with open(config_path, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value  = line.split('=', 1)
                    raw_data[key.strip()] = value.strip()
        width = int(raw_data['WIDTH'])
        height = int(raw_data['HEIGHT'])

        entry_x, entry_y = map(int, raw_data['ENTRY'].split(','))
        exit_x, exit_y = map(int, raw_data['EXIT'].split(','))

        perfect = raw_data['PERFECT'].lower == 'true'

        return Config(
            width=width,
            height=height,
            entry=(entry_x, entry_y),
            exit=(exit_x, exit_y),
            output_file=raw_data['OUTPUT_FILE'],
            perfect=perfect
        )

    except FileNotFoundError as e:
        print(f"Error: Configuration file '{config_path}' not found.")
        sys.exit(1)
    except (KeyError,  ValueError) as e:
        print(f"Error: Invalid configuration format. Missing or bad data: {e}")
        sys.exit
    