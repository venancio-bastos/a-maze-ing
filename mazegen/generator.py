import random
from typing import List, Optional, Tuple


ALL_WALLS = 15
MAX_SCALE = 6


class MazeGenerator:
    """
    Generate a maze using iterative DFS (stack-based).

    Walls encoding (bit=1 means CLOSED, bit=0 means OPEN):
        0: North, 1: East, 2: South, 3: West

    The project config requires mandatory keys including:
    WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT. :contentReference[oaicite:1]{index=1}
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        output_file: str,
        perfect: bool,
        seed: Optional[int] = None,
    ) -> None:
        """
        Initialize generator and validate mandatory config values.

        Args:
            width: Maze width (number of columns).
            height: Maze height (number of rows).
            entry: Entry coordinates (x, y).
            exit_: Exit coordinates (x, y). Named exit_ because 'exit' is a builtin.
            output_file: Output filename (e.g., "maze.txt").
            perfect: If True, maze must have exactly one path entry->exit.
            seed: Optional seed for reproducibility.

        Raises:
            ValueError: If parameters are invalid.
        """
        if not isinstance(width, int) or not isinstance(height, int):
            raise ValueError("Width and height must be integers.")
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive.")

        if (
            not isinstance(entry, tuple)
            or len(entry) != 2
            or not all(isinstance(v, int) for v in entry)
        ):
            raise ValueError("ENTRY must be a tuple of two integers: (x, y).")

        if (
            not isinstance(exit_, tuple)
            or len(exit_) != 2
            or not all(isinstance(v, int) for v in exit_)
        ):
            raise ValueError("EXIT must be a tuple of two integers: (x, y).")

        ex, ey = entry
        xx, xy = exit_

        if not (0 <= ex < width and 0 <= ey < height):
            raise ValueError("ENTRY is out of maze bounds.")
        if not (0 <= xx < width and 0 <= xy < height):
            raise ValueError("EXIT is out of maze bounds.")
        if entry == exit_:
            raise ValueError("ENTRY and EXIT must be different.")

        if not isinstance(output_file, str) or not output_file.strip():
            raise ValueError("OUTPUT_FILE must be a non-empty string.")

        if not isinstance(perfect, bool):
            raise ValueError("PERFECT must be a boolean (True/False).")

        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_
        self.output_file = output_file
        self.perfect = perfect

        if seed is not None:
            random.seed(seed)

        self.grid: List[List[int]] = [
            [ALL_WALLS for _ in range(width)] for _ in range(height)
        ]
        self.visited: List[List[bool]] = [
            [False for _ in range(width)] for _ in range(height)
        ]
        self.blocked: List[List[bool]] = [
            [False for _ in range(width)] for _ in range(height)
        ]

    def _build_42_mask(self, margin: int = 1) -> bool:
        """Build a scalable centered '42' mask (may be omitted if too small)."""
        base_42 = [
            [1, 0, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1],
        ]
        base_h = len(base_42)
        base_w = len(base_42[0])

        self.blocked = [
            [False for _ in range(self.width)] for _ in range(self.height)
        ]

        min_w = base_w + 2 * margin
        min_h = base_h + 2 * margin
        if self.width < min_w or self.height < min_h:
            print(
                "Error: Maze too small to draw '42' with margin={}. "
                "Need at least {}x{}, got {}x{}. Skipping '42' pattern."
                .format(margin, min_w, min_h, self.width, self.height)
            )
            return False

        k_w = (self.width - 2 * margin) // base_w
        k_h = (self.height - 2 * margin) // base_h
        k = min(k_w, k_h)
        k = max(1, min(k, MAX_SCALE))

        pat_w = base_w * k
        pat_h = base_h * k
        left = (self.width - pat_w) // 2
        top = (self.height - pat_h) // 2

        right_margin = self.width - (left + pat_w)
        bottom_margin = self.height - (top + pat_h)
        if left < margin or top < margin or right_margin < margin or bottom_margin < margin:
            print(
                "Error: Could not place '42' safely away from borders. "
                "Skipping '42' pattern."
            )
            return False

        for by in range(base_h):
            for bx in range(base_w):
                if base_42[by][bx] != 1:
                    continue
                for dy in range(k):
                    for dx in range(k):
                        x = left + bx * k + dx
                        y = top + by * k + dy
                        self.blocked[y][x] = True

        return True

    def _apply_42_walls(self) -> None:
        """Close all walls for 42 cells and keep wall coherence."""
        for y in range(self.height):
            for x in range(self.width):
                if not self.blocked[y][x]:
                    continue

                self.grid[y][x] = ALL_WALLS

                if y > 0:
                    self.grid[y - 1][x] |= (1 << 2)
                if x < self.width - 1:
                    self.grid[y][x + 1] |= (1 << 3)
                if y < self.height - 1:
                    self.grid[y + 1][x] |= (1 << 0)
                if x > 0:
                    self.grid[y][x - 1] |= (1 << 1)

    def _get_neighbors(self, x: int, y: int) -> List[Tuple[int, int, int, int]]:
        """Return unvisited, non-blocked neighbors with wall-bit info."""
        neighbors: List[Tuple[int, int, int, int]] = []

        if y > 0 and not self.visited[y - 1][x] and not self.blocked[y - 1][x]:
            neighbors.append((x, y - 1, 0, 2))  # North

        if (
            x < self.width - 1
            and not self.visited[y][x + 1]
            and not self.blocked[y][x + 1]
        ):
            neighbors.append((x + 1, y, 1, 3))  # East

        if (
            y < self.height - 1
            and not self.visited[y + 1][x]
            and not self.blocked[y + 1][x]
        ):
            neighbors.append((x, y + 1, 2, 0))  # South

        if x > 0 and not self.visited[y][x - 1] and not self.blocked[y][x - 1]:
            neighbors.append((x - 1, y, 3, 1))  # West

        return neighbors

    def generate(self, margin: int = 1) -> None:
        """
        Generate the maze using iterative DFS starting from ENTRY.

        Note:
            PERFECT and OUTPUT_FILE are stored here for later steps
            (loop-handling + writing output file). :contentReference[oaicite:2]{index=2}
        """
        start_x, start_y = self.entry

        self._build_42_mask(margin=margin)

        if self.blocked[start_y][start_x]:
            raise ValueError("ENTRY is inside the '42' pattern.")

        if self.blocked[self.exit[1]][self.exit[0]]:
            raise ValueError("EXIT is inside the '42' pattern.")

        self.grid = [
            [ALL_WALLS for _ in range(self.width)] for _ in range(self.height)
        ]
        self.visited = [
            [False for _ in range(self.width)] for _ in range(self.height)
        ]

        self._dfs_iterative(start_x, start_y)
        self._apply_42_walls()

    def _dfs_iterative(self, start_x: int, start_y: int) -> None:
        """Iterative DFS (stack-based) to avoid recursion depth issues."""
        self.visited[start_y][start_x] = True
        stack: List[Tuple[int, int]] = [(start_x, start_y)]

        while stack:
            x, y = stack[-1]

            neighbors = self._get_neighbors(x, y)
            random.shuffle(neighbors)

            if not neighbors:
                stack.pop()
                continue

            nx, ny, b_curr, b_next = neighbors[0]

            self.grid[y][x] &= ~(1 << b_curr)
            self.grid[ny][nx] &= ~(1 << b_next)

            self.visited[ny][nx] = True
            stack.append((nx, ny))

    def to_hex_string(self) -> str:
        """Convert the grid to hex lines (one row per line)."""
        return "\n".join(
            "".join(format(cell, "x") for cell in row) for row in self.grid
        )

    def get_grid(self) -> List[List[int]]:
        """Return the maze grid."""
        return self.grid
