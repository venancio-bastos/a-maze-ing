"""Shared constants for the maze package."""

from typing import Final

ALL_WALLS: Final[int] = 15
MAX_SCALE: Final[int] = 2

# (dx, dy, bit_current_cell, bit_next_cell)
DIRS: Final[list[tuple[int, int, int, int]]] = [
    (0, -1, 0, 2),   # North
    (1, 0, 1, 3),    # East
    (0, 1, 2, 0),    # South
    (-1, 0, 3, 1),   # West
]
