"""DFS-based maze carving."""

from __future__ import annotations

import random
from typing import List, Tuple

from .constants import DIRS
from .grid import MazeGrid


class DFSMazeCarver:
    """Carve a maze with iterative DFS."""

    def __init__(self, rng: random.Random) -> None:
        """Store the random generator."""
        self.rng = rng

    def carve(
        self,
        grid: MazeGrid,
        start_x: int,
        start_y: int,
        blocked: List[List[bool]],
    ) -> None:
        """Carve reachable free cells starting from one cell."""
        visited = [
            [False for _ in range(grid.width)]
            for _ in range(grid.height)
        ]
        visited[start_y][start_x] = True

        stack: List[Tuple[int, int]] = [(start_x, start_y)]

        while stack:
            x, y = stack[-1]
            neighbors: List[Tuple[int, int, int, int]] = []

            for dx, dy, b_curr, b_next in DIRS:
                nx, ny = x + dx, y + dy
                if not grid.in_bounds(nx, ny):
                    continue
                if visited[ny][nx]:
                    continue
                if blocked[ny][nx]:
                    continue
                neighbors.append((nx, ny, b_curr, b_next))

            self.rng.shuffle(neighbors)

            if not neighbors:
                stack.pop()
                continue

            nx, ny, b_curr, b_next = neighbors[0]
            grid.break_wall(x, y, nx, ny, b_curr, b_next)
            visited[ny][nx] = True
            stack.append((nx, ny))
