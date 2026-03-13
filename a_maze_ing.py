import sys
from typing import Dict, Any
from src.maze_app import MazeApp

def parse_config(filename: str) -> Dict[str, Any]:
    """
    Reads the config file and converts the string values into their proper Python types.
    """
    config: Dict[str, Any] = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                key, val = line.split('=')
                key = key.strip()
                val = val.strip()
                
                # Convert values to the correct types based on the key
                if key in ['WIDTH', 'HEIGHT']:
                    config[key] = int(val)
                elif key in ['ENTRY', 'EXIT']:
                    coords = val.split(',')
                    config[key] = (int(coords[0].strip()), int(coords[1].strip()))
                elif key == 'PERFECT':
                    config[key] = val.lower() == 'true'
                elif key == 'OUTPUT_FILE':
                    config[key] = val          
    except Exception as e:
        print(f"Error reading config file: {e}")
        sys.exit(1)
    return config

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 -m src.a_maze_ing <config_file>")
        sys.exit(1)
        
    config_file: str = sys.argv[1]
    config: Dict[str, Any] = parse_config(config_file)
    
    # Pass the entire config dictionary to the MazeApp
    app = MazeApp(800, 600, "A-Maze-ing", config)
    app.run()

if __name__ == "__main__":
    main()