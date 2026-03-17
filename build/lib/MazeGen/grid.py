"""Grid storage and wall operations."""

from __future__ import annotations

from typing import List

from .constants import ALL_WALLS


class MazeGrid:
    """Store maze cells and low-level wall operations."""

    def __init__(self, width: int, height: int) -> None:
        """Create a grid filled with closed cells."""
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive.")
        self.width = width
        self.height = height
        self.cells: List[List[int]] = []
        self.reset()

    def reset(self) -> None:
        """Reset all cells to fully closed walls."""
        self.cells = [
            [ALL_WALLS for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if coordinates are inside the grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def break_wall(
        self,
        x: int,
        y: int,
        nx: int,
        ny: int,
        b_curr: int,
        b_next: int,
    ) -> None:
        """Open the wall between two adjacent cells."""
        self.cells[y][x] &= ~(1 << b_curr)
        self.cells[ny][nx] &= ~(1 << b_next)

    def to_hex_string(self) -> str:
        """Return the grid as hexadecimal rows."""
        return "\n".join(
            "".join(format(cell, "x") for cell in row)
            for row in self.cells
        )
