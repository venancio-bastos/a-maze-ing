import sys
from typing import Any, Dict

from src import MazeApp


MANDATORY_KEYS = [
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
]
OPTIONAL_KEYS = ["SEED"]
ALLOWED_KEYS = set(MANDATORY_KEYS + OPTIONAL_KEYS)


def parse_config(filename: str) -> Dict[str, Any]:
    """Parse and validate the configuration file."""
    config: Dict[str, Any] = {}

    try:
        with open(filename, "r", encoding="utf-8") as file:
            for raw_line in file:
                line = raw_line.strip()

                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    raise ValueError(f"Invalid format (missing '='): '{line}'")

                key, value = line.split("=", 1)
                key = key.strip().upper()
                value = value.strip()

                if key not in ALLOWED_KEYS:
                    raise ValueError(f"Unknown configuration key: '{key}'")
                if key in config:
                    raise ValueError(f"Duplicate configuration key: '{key}'")

                if key in ["WIDTH", "HEIGHT"]:
                    try:
                        config[key] = int(value)
                    except ValueError as exc:
                        raise ValueError(f"{key} must be an integer.") from exc
                elif key in ["ENTRY", "EXIT"]:
                    coords = value.split(",")
                    if len(coords) != 2:
                        raise ValueError(f"{key} must use the format x,y.")
                    try:
                        config[key] = (
                            int(coords[0].strip()),
                            int(coords[1].strip()),
                        )
                    except ValueError as exc:
                        raise ValueError(
                            f"Coordinates for {key} must be integers."
                        ) from exc
                elif key == "PERFECT":
                    lowered = value.lower()
                    if lowered not in ["true", "false"]:
                        raise ValueError("PERFECT must be 'True' or 'False'.")
                    config[key] = lowered == "true"
                elif key == "SEED":
                    try:
                        config[key] = int(value)
                    except ValueError as exc:
                        raise ValueError("SEED must be an integer.") from exc
                else:
                    if not value:
                        raise ValueError(f"{key} cannot be empty.")
                    config[key] = value

        for mandatory_key in MANDATORY_KEYS:
            if mandatory_key not in config:
                raise ValueError(
                    f"Missing mandatory configuration: '{mandatory_key}'"
                )

    except FileNotFoundError:
        print(f"Error: The configuration file '{filename}' was not found.")
        sys.exit(1)
    except Exception as exc:
        print(f"Configuration Error: {exc}")
        sys.exit(1)

    return config


def main() -> None:
    """Read the config, create the app, and launch it."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]
    config = parse_config(config_file)

    try:
        app = MazeApp(800, 600, "A-Maze-ing", config)
        app.run()
    except Exception as exc:
        print(f"Maze Generation error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
