"""Shortest path solver for a maze."""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Tuple

from .constants import DIRS

Grid = List[List[int]]
Coord = Tuple[int, int]

DIR_LETTERS: Dict[Tuple[int, int], str] = {
    (0, -1): "N",
    (1, 0): "E",
    (0, 1): "S",
    (-1, 0): "W",
}


class MazeSolver:
    """Solve the maze with BFS."""

    def __init__(
        self,
        grid: Grid,
        entry: Coord,
        exit_: Coord,
        blocked: Optional[List[List[bool]]] = None,
    ) -> None:
        """Store maze data and validate dimensions."""
        if not grid or not grid[0]:
            raise ValueError("Grid cannot be empty.")

        self.height = len(grid)
        self.width = len(grid[0])

        if any(len(row) != self.width for row in grid):
            raise ValueError("Grid must be rectangular.")

        self.grid = grid
        self.entry = entry
        self.exit = exit_
        self.blocked = blocked

        sx, sy = entry
        ex, ey = exit_

        if not self._in_bounds(sx, sy):
            raise ValueError(f"ENTRY {entry} is out of bounds.")
        if not self._in_bounds(ex, ey):
            raise ValueError(f"EXIT {exit_} is out of bounds.")

        if blocked is not None:
            if len(blocked) != self.height:
                raise ValueError("Blocked mask height does not match grid.")
            if any(len(row) != self.width for row in blocked):
                raise ValueError("Blocked mask width does not match grid.")
            if blocked[sy][sx]:
                raise ValueError("ENTRY is inside a blocked cell.")
            if blocked[ey][ex]:
                raise ValueError("EXIT is inside a blocked cell.")

    def _in_bounds(self, x: int, y: int) -> bool:
        """Return True if one cell is inside the grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def _wall_open(self, x: int, y: int, bit: int) -> bool:
        """Return True if a wall bit is open."""
        return (self.grid[y][x] & (1 << bit)) == 0

    def solve(self) -> Optional[str]:
        """Return the shortest path as N/E/S/W letters."""
        if self.entry == self.exit:
            return ""

        queue = deque([self.entry])
        came_from: Dict[Coord, Coord] = {}
        move_taken: Dict[Coord, str] = {}
        visited = {self.entry}

        while queue:
            x, y = queue.popleft()

            if (x, y) == self.exit:
                return self._reconstruct(came_from, move_taken)

            for dx, dy, b_curr, _b_next in DIRS:
                nx, ny = x + dx, y + dy

                if not self._in_bounds(nx, ny):
                    continue
                if self.blocked is not None and self.blocked[ny][nx]:
                    continue
                if (nx, ny) in visited:
                    continue
                if not self._wall_open(x, y, b_curr):
                    continue

                visited.add((nx, ny))
                came_from[(nx, ny)] = (x, y)
                move_taken[(nx, ny)] = DIR_LETTERS[(dx, dy)]
                queue.append((nx, ny))

        return None

    def _reconstruct(
        self,
        came_from: Dict[Coord, Coord],
        move_taken: Dict[Coord, str],
    ) -> str:
        """Build the final path string."""
        cur = self.exit
        letters: List[str] = []

        while cur != self.entry:
            if cur not in came_from:
                return ""
            letters.append(move_taken[cur])
            cur = came_from[cur]

        letters.reverse()
        return "".join(letters)
