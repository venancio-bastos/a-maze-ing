"""Builder for the blocked '42' pattern."""

from __future__ import annotations

from typing import List

from .constants import MAX_SCALE


class Mask42Builder:
    """Build a centered scalable '42' blocked mask."""

    def __init__(self, margin: int = 1) -> None:
        """Store the minimum border margin."""
        if margin < 0:
            raise ValueError("margin must be >= 0.")
        self.margin = margin

    def build(self, width: int, height: int) -> List[List[bool]]:
        """Return blocked[y][x] where True means part of '42'."""
        base_42 = [
            [1, 0, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1],
        ]
        base_h = len(base_42)
        base_w = len(base_42[0])

        blocked = [
            [False for _ in range(width)]
            for _ in range(height)
        ]

        min_w = base_w + (2 * self.margin)
        min_h = base_h + (2 * self.margin)
        if width < min_w or height < min_h:
            print(
                "[42] Warning: maze too small for the '42' pattern. "
                f"Need at least {min_w}x{min_h}, got {width}x{height}. "
                "Skipping pattern."
            )
            return blocked

        scale_w = (width - (2 * self.margin)) // base_w
        scale_h = (height - (2 * self.margin)) // base_h
        scale = max(1, min(scale_w, scale_h, MAX_SCALE))

        pat_w = base_w * scale
        pat_h = base_h * scale
        left = (width - pat_w) // 2
        top = (height - pat_h) // 2

        right_margin = width - (left + pat_w)
        bottom_margin = height - (top + pat_h)

        if (
            left < self.margin
            or top < self.margin
            or right_margin < self.margin
            or bottom_margin < self.margin
        ):
            print(
                "[42] Warning: cannot place the '42' pattern safely. "
                "Skipping pattern."
            )
            return blocked

        for by in range(base_h):
            for bx in range(base_w):
                if base_42[by][bx] != 1:
                    continue
                for dy in range(scale):
                    for dx in range(scale):
                        x = left + (bx * scale) + dx
                        y = top + (by * scale) + dy
                        blocked[y][x] = True

        return blocked
