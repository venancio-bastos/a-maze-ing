from __future__ import annotations
from MazeGen.generator import MazeGenerator
from MazeGen.solver import MazeSolver


def main() -> None:
    """Run a simple test for maze generation and solving."""
    width = 20
    height = 15
    entry = (0, 0)
    exit_ = (19, 14)
    seed = 42
    perfect = False
    margin = 1

    generator = MazeGenerator(
        width=width,
        height=height,
        entry=entry,
        exit_=exit_,
        output_file="unused.txt",
        perfect=perfect,
        seed=seed,
    )

    generator.generate(margin=margin)

    grid = generator.get_grid()
    blocked = getattr(generator, "blocked", None)

    solver = MazeSolver(
        grid=grid,
        entry=entry,
        exit_=exit_,
        blocked=blocked,
    )
    path = solver.solve()

    print("=== HEX GRID ===")
    print(generator.to_hex_string())

    print("\n=== PATH ===")
    if path is None:
        print("No path found.")
    else:
        print(path)
        print(f"Path length: {len(path)}")


if __name__ == "__main__":
    main()
