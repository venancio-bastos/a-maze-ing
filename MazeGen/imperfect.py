"""Post-processing for imperfect mazes."""

from __future__ import annotations

import random
from typing import List, Optional

from .constants import DIRS
from .grid import MazeGrid


class LoopAdder:
    """Add loops while avoiding 3x3 fully open areas."""

    def __init__(self, rng: random.Random) -> None:
        """Store the random generator."""
        self.rng = rng

    def _is_open_to(self, grid: MazeGrid, x: int, y: int, bit: int) -> bool:
        """Return True if the wall in one direction is open."""
        return (grid.cells[y][x] & (1 << bit)) == 0

    def _creates_open_3x3(
        self,
        grid: MazeGrid,
        blocked: List[List[bool]],
        cx: int,
        cy: int,
    ) -> bool:
        """Return True if a fully open 3x3 area exists around one cell."""
        for ox in range(cx - 2, cx + 1):
            for oy in range(cy - 2, cy + 1):
                all_valid = True

                for dy in range(3):
                    for dx in range(3):
                        px, py = ox + dx, oy + dy
                        if not grid.in_bounds(px, py) or blocked[py][px]:
                            all_valid = False
                            break
                    if not all_valid:
                        break

                if not all_valid:
                    continue

                open_area = True

                for dy in range(3):
                    for dx in range(2):
                        px, py = ox + dx, oy + dy
                        if not self._is_open_to(grid, px, py, 1):
                            open_area = False
                            break
                    if not open_area:
                        break

                if not open_area:
                    continue

                for dy in range(2):
                    for dx in range(3):
                        px, py = ox + dx, oy + dy
                        if not self._is_open_to(grid, px, py, 2):
                            open_area = False
                            break
                    if not open_area:
                        break

                if open_area:
                    return True

        return False

    def _close_wall(
        self,
        grid: MazeGrid,
        x: int,
        y: int,
        nx: int,
        ny: int,
        b_curr: int,
        b_next: int,
    ) -> None:
        """Restore a wall between two cells."""
        grid.cells[y][x] |= (1 << b_curr)
        grid.cells[ny][nx] |= (1 << b_next)

    def add_loops(
        self,
        grid: MazeGrid,
        blocked: List[List[bool]],
        loops: Optional[int] = None,
        max_tries_multiplier: int = 30,
    ) -> None:
        """Open extra walls without creating a 3x3 open block."""
        free_cells = sum(
            1
            for y in range(grid.height)
            for x in range(grid.width)
            if not blocked[y][x]
        )
        if free_cells <= 1:
            return

        if loops is None:
            loops = max(1, free_cells // 20)

        tries = 0
        opened = 0
        max_tries = loops * max_tries_multiplier

        while opened < loops and tries < max_tries:
            tries += 1

            x = self.rng.randrange(grid.width)
            y = self.rng.randrange(grid.height)
            if blocked[y][x]:
                continue

            dx, dy, b_curr, b_next = self.rng.choice(DIRS)
            nx, ny = x + dx, y + dy

            if not grid.in_bounds(nx, ny):
                continue
            if blocked[ny][nx]:
                continue

            if (grid.cells[y][x] & (1 << b_curr)) == 0:
                continue

            grid.break_wall(x, y, nx, ny, b_curr, b_next)

            if (
                self._creates_open_3x3(grid, blocked, x, y)
                or self._creates_open_3x3(grid, blocked, nx, ny)
            ):
                self._close_wall(grid, x, y, nx, ny, b_curr, b_next)
                continue

            opened += 1
