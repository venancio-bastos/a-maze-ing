import sys
from typing import Dict, Any
from src.maze_app import MazeApp


def parse_config(filename: str) -> Dict[str, Any]:
    """
    Reads the config file, validates formatting strictly,
    and converts string values into proper Python types.
    """
    config: Dict[str, Any] = {}
    mandatory_keys = [
        'WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE', 'PERFECT'
    ]

    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith('#'):
                    continue

                if '=' not in line:
                    raise ValueError(f"Invalid format (missing '='): '{line}'")

                key, val = line.split('=', 1)
                key = key.strip().upper()
                val = val.strip()

                if key in ['WIDTH', 'HEIGHT']:
                    if not val.isdigit():
                        raise ValueError(f"{key} must be an integer.")
                    config[key] = int(val)
                elif key in ['ENTRY', 'EXIT']:
                    coords = val.split(',')
                    if len(coords) != 2:
                        raise ValueError(f"{key} must be a valid 'x,y' tuple.")
                    try:
                        config[key] = (
                            int(coords[0].strip()), int(coords[1].strip())
                        )
                    except ValueError:
                        raise ValueError(
                            f"Coordinates for {key} must be integers."
                        )
                elif key == 'PERFECT':
                    if val.lower() not in ['true', 'false']:
                        raise ValueError("PERFECT must be 'True' or 'False'.")
                    config[key] = val.lower() == 'true'
                else:
                    config[key] = val

        for m_key in mandatory_keys:
            if m_key not in config:
                raise ValueError(f"Missing mandatory configuration: '{m_key}'")

    except FileNotFoundError:
        print(f"Error: The configuration file '{filename}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)

    return config


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 -m src.a_maze_ing <config_file>")
        sys.exit(1)

    config_file: str = sys.argv[1]
    config: Dict[str, Any] = parse_config(config_file)

    # Pass the entire config dictionary to the MazeApp
    try:
        app = MazeApp(800, 600, "A-Maze-ing", config)
        app.run()
    except Exception as e:
        print(f"Maze Generation error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
