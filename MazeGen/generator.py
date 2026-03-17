"""High-level reusable maze generator."""

from __future__ import annotations

import random
from collections import deque
from typing import List, Optional, Tuple

from .carver_dfs import DFSMazeCarver
from .constants import DIRS
from .grid import MazeGrid
from .imperfect import LoopAdder
from .mask_42 import Mask42Builder
from .solver import MazeSolver


Coord = Tuple[int, int]


class MazeGenerator:
    """Generate a maze and expose its structure and solution."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: Coord,
        exit_: Coord,
        output_file: str,
        perfect: bool,
        seed: Optional[int] = None,
    ) -> None:
        """Validate and store maze settings."""
        self._validate(width, height, entry, exit_, output_file, perfect)

        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_
        self.output_file = output_file
        self.perfect = perfect
        self.seed = seed

        self.rng = random.Random(seed)
        self.grid = MazeGrid(width, height)
        self.blocked: List[List[bool]] = [
            [False for _ in range(width)]
            for _ in range(height)
        ]

        self._carver = DFSMazeCarver(self.rng)
        self._loop_adder = LoopAdder(self.rng)

    @staticmethod
    def _validate(
        width: int,
        height: int,
        entry: Coord,
        exit_: Coord,
        output_file: str,
        perfect: bool,
    ) -> None:
        """Validate the constructor arguments."""
        if not isinstance(width, int) or not isinstance(height, int):
            raise ValueError("Width and height must be integers.")
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive.")

        if (
            not isinstance(entry, tuple)
            or len(entry) != 2
            or not all(isinstance(v, int) for v in entry)
        ):
            raise ValueError("ENTRY must be a tuple of two integers.")
        if (
            not isinstance(exit_, tuple)
            or len(exit_) != 2
            or not all(isinstance(v, int) for v in exit_)
        ):
            raise ValueError("EXIT must be a tuple of two integers.")

        if entry == exit_:
            raise ValueError("ENTRY and EXIT must be different.")

        entry_x, entry_y = entry
        exit_x, exit_y = exit_

        if not (0 <= entry_x < width and 0 <= entry_y < height):
            raise ValueError("ENTRY is out of maze bounds.")
        if not (0 <= exit_x < width and 0 <= exit_y < height):
            raise ValueError("EXIT is out of maze bounds.")

        if not isinstance(output_file, str) or not output_file.strip():
            raise ValueError("OUTPUT_FILE must be a non-empty string.")

        if not isinstance(perfect, bool):
            raise ValueError("PERFECT must be a boolean.")

    def _check_connectivity(self) -> bool:
        """Return True if all free cells are reachable from the entry."""
        free_cells = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if not self.blocked[y][x]
        ]

        if not free_cells:
            return True

        start_x, start_y = self.entry
        visited = [
            [False for _ in range(self.width)]
            for _ in range(self.height)
        ]
        visited[start_y][start_x] = True

        queue = deque([(start_x, start_y)])
        count = 1

        while queue:
            x, y = queue.popleft()
            cell_value = self.grid.cells[y][x]

            for dx, dy, b_curr, _b_next in DIRS:
                if (cell_value & (1 << b_curr)) != 0:
                    continue

                nx, ny = x + dx, y + dy
                if not self.grid.in_bounds(nx, ny):
                    continue
                if visited[ny][nx]:
                    continue
                if self.blocked[ny][nx]:
                    continue

                visited[ny][nx] = True
                count += 1
                queue.append((nx, ny))

        return count == len(free_cells)

    def generate(self, margin: int = 1) -> None:
        """Run the full maze generation pipeline."""
        self.blocked = Mask42Builder(margin=margin).build(
            self.width,
            self.height,
        )

        start_x, start_y = self.entry
        exit_x, exit_y = self.exit

        if self.blocked[start_y][start_x]:
            raise ValueError("ENTRY is inside the '42' pattern.")
        if self.blocked[exit_y][exit_x]:
            raise ValueError("EXIT is inside the '42' pattern.")

        self.grid.reset()
        self._carver.carve(self.grid, start_x, start_y, self.blocked)

        if not self._check_connectivity():
            raise RuntimeError(
                "Maze connectivity error: some free cells are unreachable."
            )

        if not self.perfect:
            self._loop_adder.add_loops(self.grid, self.blocked)

    def solve(self) -> Optional[str]:
        """Return one shortest valid solution."""
        solver = MazeSolver(
            grid=self.grid.cells,
            entry=self.entry,
            exit_=self.exit,
            blocked=self.blocked,
        )
        return solver.solve()

    def get_solution(self) -> Optional[str]:
        """Return one shortest valid solution."""
        return self.solve()

    def to_hex_string(self) -> str:
        """Return the maze grid as hexadecimal rows."""
        return self.grid.to_hex_string()

    def get_grid(self) -> List[List[int]]:
        """Return the raw maze grid."""
        return [row[:] for row in self.grid.cells]

    def get_blocked_mask(self) -> List[List[bool]]:
        """Return the blocked '42' mask."""
        return [row[:] for row in self.blocked]

    def build_output_text(self) -> str:
        """Return the text content expected by the project output."""
        solution = self.solve()
        if solution is None:
            raise RuntimeError("No valid solution exists for this maze.")

        entry_line = f"{self.entry[0]},{self.entry[1]}"
        exit_line = f"{self.exit[0]},{self.exit[1]}"
        return (
            f"{self.to_hex_string()}\n\n"
            f"{entry_line}\n"
            f"{exit_line}\n"
            f"{solution}\n"
        )
