# Amazing

This part of the project creates a maze as hexadecimal cells, keeps a visible `42` pattern using fully closed cells, supports both perfect and imperfect mazes, and computes one shortest valid path from the entry to the exit.

The code is written as a reusable Python package. The main class is `MazeGenerator`, which handles maze creation, validation, solving, and final output formatting.

---

## Project goal

The goal of this project is to build a maze generator that:

- creates a valid maze grid
- writes the maze using hexadecimal values
- supports a perfect maze or an imperfect maze
- keeps a visible `42` pattern inside the maze
- guarantees that all non-blocked cells are reachable
- finds one shortest valid path from entry to exit
- produces output in the expected project format

---

## Main idea

Each cell of the maze stores its four walls inside one hexadecimal value.

The four directions are:

- North
- East
- South
- West

Each wall is stored as one bit:

- bit 0 = North
- bit 1 = East
- bit 2 = South
- bit 3 = West

If a bit is `1`, that wall is closed.  
If a bit is `0`, that wall is open.

So:

- `15` in decimal is `1111` in binary, which means all four walls are closed
- opening a wall means changing its bit from `1` to `0`

This is the base idea of the whole project.

---

## Project structure

```text
.
├── Makefile
├── pyproject.toml
├── config.txt
├── mlx-2.2-py3-none-any.whl
├── src/
│   ├── a_maze_ing.py
│   └── maze_app.py
└── MazeGen/
    ├── __init__.py
    ├── carver_dfs.py
    ├── constants.py
    ├── generator.py
    ├── grid.py
    ├── imperfect.py
    ├── mask_42.py
    └── solver.py
```

## Quick Start

The easiest way to run the project with the graphical interface is using the provided `Makefile`.

It automatically:
- creates a virtual environment
- installs the required `pyproject.toml` setup
- installs the MiniLibX (MLX) wheel
- launches the application

Run this command at the root of the project:

```bash
make run
```

To clean up the environment run:
```bash
make clean || make fclean
```

# Files Explanation

## `a_maze_ing.py`

This is the main entry point for the graphical application.

Its job is to prepare the environment before the visual engine starts.

### Main responsibilities

- read the `config.txt` file
- parse raw strings into proper Python data types (integers, tuples, booleans)
- validate command-line arguments
- instantiate and run the `MazeApp`

---

## `maze_app.py`

This file contains the `MazeApp` class.

Its job is to handle the MiniLibX (MLX) window, render the maze to the screen, and manage keyboard events.

### How rendering works

Drawing pixel by pixel directly to the screen is slow. Instead, this class:
1. creates an invisible image in the computer's RAM
2. calculates the exact memory offset for each pixel using a 1D array
3. pushes the fully drawn image to the window in one go (avoiding flickering)

### Important methods

#### `put_pixel(x, y, color)`

Injects a 32-bit color directly into the RAM address of a specific pixel using bitwise shifts.

#### `fill_area(start_x, start_y, width, height, color)`

Acts as the base geometric tool. Everything on the screen (walls, background, path) is drawn as a rectangle using this method.

#### `draw_maze(wall_color)`

Translates the generator's grid into physical pixels. 
It checks the bitwise values of each cell (`1` for North, `2` for East, `4` for South, `8` for West) and draws the corresponding wall rectangles. It also fills the `42` blocked mask with a solid color.

#### `draw_all()`

Uses the Painter's Algorithm to render the scene from back to front:
- draws the background
- draws the maze walls and the `42` pattern
- draws the solution path (if enabled)
- draws the entry and exit points on top

#### `handle_key(keycode, params)`

Listens for keyboard inputs to regenerate the maze, toggle the solution path, change color palettes, or exit the program cleanly.

## `constants.py`

This file contains shared constants used in the whole package.

### Important values

#### `ALL_WALLS = 15`

This means a cell starts with all walls closed.

#### `MAX_SCALE = 2`

This limits the size of the `42` pattern when the maze is large.

#### `DIRS`

This defines the four directions and the matching wall bits.

Each item in `DIRS` looks like this:

```python
(dx, dy, bit_current_cell, bit_next_cell)
```

Example:

```python
(0, -1, 0, 2)
```

This means moving North:

- `dx = 0`
- `dy = -1`
- the current cell uses bit `0` for North
- the next cell uses bit `2` for South

This keeps the wall data consistent between neighboring cells.

---

## `grid.py`

This file contains the `MazeGrid` class.

Its job is to store the maze cells and provide low-level wall operations.

### Main responsibilities

- create the grid
- reset all cells to fully closed
- check if coordinates are inside the maze
- open a wall between two cells
- export the maze as hexadecimal text

### Important methods

#### `reset()`

Fills the whole maze with `15`, meaning all walls are closed.

#### `in_bounds(x, y)`

Checks if a cell is inside the maze boundaries.

#### `break_wall(x, y, nx, ny, b_curr, b_next)`

Opens the wall between two neighboring cells.

It updates both cells:

- the wall bit in the current cell
- the opposite wall bit in the next cell

This is very important because wall information must stay coherent.

#### `to_hex_string()`

Converts the maze grid into the required hexadecimal text format.

---

## `carver_dfs.py`

This file contains the `DFSMazeCarver` class.

It uses iterative DFS to carve the main maze.

DFS stands for **Depth-First Search**.

### Why DFS is used here

- it is simple
- it is a classic maze generation method
- it creates a perfect maze structure first
- it is easy to control with a stack

### How it works

1. start from the entry cell
2. mark the current cell as visited
3. look for unvisited valid neighbors
4. choose one neighbor randomly
5. break the wall to that neighbor
6. move forward
7. if no neighbor exists, backtrack using the stack

Because it only moves to unvisited cells, the first carved structure has no cycles.

This is why it naturally creates a perfect maze.

Blocked cells from the `42` pattern are never carved.

---

## `imperfect.py`

This file contains the `LoopAdder` class.

Its job is to make the maze imperfect by opening extra walls after DFS carving is finished.

A perfect maze has only one unique path between two cells.

An imperfect maze has extra connections, so loops can appear.

### How loops are added

1. choose a random cell
2. choose a random direction
3. check that the wall is currently closed
4. open that wall
5. verify that this does not create a forbidden fully open `3x3` area
6. keep the change if valid, otherwise undo it

### Important idea

Adding a loop means opening an extra closed wall between two cells.

It does not mean drawing a special shape directly.

It means creating one more connection in the maze graph, which creates a cycle.

### Why the `3x3` check is needed

The subject does not allow a fully open `3x3` area.

So after opening a wall, the code checks nearby `3x3` zones.

If the new opening would create a full open `3x3` block, the wall is closed again.

This keeps the maze valid.

---

## `mask_42.py`

This file contains the `Mask42Builder` class.

Its job is to create the `42` pattern inside the maze.

The pattern is stored as blocked cells:

- `True` means the cell belongs to the `42`
- `False` means the cell is free

Blocked cells are never carved, so they stay fully closed.

This is how the visible `42` is preserved in the final maze.

### Important steps

1. define a base `42` pattern
2. check if the maze is large enough
3. compute a safe scale
4. center the pattern inside the maze
5. mark the pattern cells as blocked

If the maze is too small, the code skips the pattern and prints a warning.

This matches the subject requirement that the pattern may be removed safely for very small mazes.

---

## `solver.py`

This file contains the `MazeSolver` class.

It finds one shortest valid path from entry to exit.

It uses BFS, which means **Breadth-First Search**.

### Why BFS is used

- the maze graph is unweighted
- BFS guarantees a shortest path in an unweighted graph

### How it works

1. start from the entry
2. explore all reachable neighbors layer by layer
3. store where each cell came from
4. stop when the exit is reached
5. rebuild the path by walking backward from exit to entry

The returned path is written as letters:

- `N`
- `E`
- `S`
- `W`

Blocked cells from the `42` mask are ignored during solving.

---

## `generator.py`

This is the main file of the project.

It contains the `MazeGenerator` class, which is the reusable public interface of the package.

This class combines all the other parts:

- grid creation
- `42` pattern building
- DFS carving
- optional loop addition
- connectivity checking
- solving
- output text generation

### Important methods

#### `__init__(...)`

Stores the maze settings:

- width
- height
- entry
- exit
- output file name
- perfect or imperfect mode
- optional random seed

It also validates the inputs.

#### `_validate(...)`

Checks that:

- width and height are positive integers
- entry and exit are valid coordinates
- entry and exit are different
- the output file name is valid
- the perfect flag is boolean

#### `_check_connectivity()`

Runs a BFS from the entry to confirm that all free cells are reachable.

This is important because the maze must not contain isolated usable cells.

#### `generate(margin=1)`

Runs the full generation pipeline:

1. build the `42` mask
2. verify that entry and exit are not inside the pattern
3. reset the grid
4. carve the maze with DFS
5. check connectivity
6. if the maze is imperfect, add loops

#### `solve()`

Uses `MazeSolver` to get one shortest valid solution.

#### `to_hex_string()`

Returns the maze grid as hexadecimal rows.

#### `build_output_text()`

Builds the final text exactly in the required output format.

---

## `__init__.py`

This file makes the package easier to import.

It exports:

- `MazeGenerator`
- `MazeSolver`

So the package has a clean public interface.

---

# How the Maze Is Generated

The full generation process is:

1. create a grid where all cells are fully closed
2. build the blocked `42` mask
3. start DFS from the entry cell
4. carve paths only through non-blocked cells
5. confirm that every free cell is reachable
6. if imperfect mode is requested, open some extra walls
7. solve the maze with BFS
8. export the final text

---

# Perfect vs Imperfect Maze

## Perfect Maze

A perfect maze has:

- no cycles
- exactly one unique path between reachable cells

In this project, the DFS carved structure is the perfect base maze.

## Imperfect Maze

An imperfect maze allows:

- loops
- more than one possible route between some cells

In this project, imperfect mode is created by opening extra closed walls after DFS carving.

---

# About Loops

A common question is: what does "adding a loop" really mean?

It means opening one extra wall between two neighboring cells that were not directly connected before.

That new connection creates a cycle in the maze graph.

So yes, in simple words:

- adding a loop means breaking or opening an extra wall

But this is done carefully:

- only between valid neighbors
- not through blocked `42` cells
- not if it creates a forbidden fully open `3x3` area

---

# About the `42` Pattern

The `42` pattern is not drawn as decoration.

It is made using fully closed blocked cells.

This means:

- DFS never carves these cells
- loop addition never opens them
- BFS never walks through them

As a result, the `42` shape remains visible inside the maze.

If the maze is too small, the pattern is skipped with a warning.

---

# Output Format

The final output text looks like this:

```text
<maze in hexadecimal rows>

<entry_x>,<entry_y>
<exit_x>,<exit_y>
<solution>
```

Example:

```text
ffff
a53c
98ef

0,0
3,2
EESSWN
```

### Meaning

1. the maze is written row by row in hexadecimal
2. then one empty line
3. then the entry coordinates
4. then the exit coordinates
5. then one shortest valid path using `N`, `E`, `S`, `W`

---

# Reusability

The code is designed to be reusable.

The main reusable class is:

```python
MazeGenerator
```

This makes the project easier to:

- test
- extend
- import into another script
- separate from a command-line interface if needed later

This is better than putting all logic in one long script.

---

# Validation and Safety

The project includes several checks to avoid invalid mazes.

Examples:

- width and height must be positive
- entry and exit must be inside the maze
- entry and exit must be different
- entry and exit must not be inside the `42` pattern
- grid must stay coherent between neighboring cells
- all free cells must be reachable
- fully open `3x3` areas are prevented in imperfect mode

These checks make the generator more robust.

---

# Why These Algorithms Were Chosen

## DFS for generation

DFS is a very common maze generation algorithm because:

- it is simple to implement
- it creates natural maze paths
- it produces a perfect maze structure first
- it works well with randomness

## BFS for solving

BFS is used because:

- the maze acts like an unweighted graph
- BFS guarantees a shortest path
- it is easy to reconstruct the path afterward

---

# Important Concepts Used in the Code

## Bitwise representation

Each cell uses four bits to store four walls.

This is compact and efficient.

## Graph thinking

The maze can be seen as a graph:

- cells are nodes
- open walls are edges

DFS builds the graph.  
BFS solves the graph.  
Loop addition adds extra edges.

## Masking

The `42` pattern is implemented as a blocked mask, which is a clean way to protect special cells during generation and solving.

## Reproducibility

The generator uses `random.Random(seed)`.

This means:

- same seed gives the same maze
- this is useful for testing and debugging

---

# Example Usage

```python
from amazing import MazeGenerator

generator = MazeGenerator(
    width=20,
    height=12,
    entry=(0, 0),
    exit_=(19, 11),
    output_file="maze.txt",
    perfect=True,
    seed=42,
)

generator.generate()
text = generator.build_output_text()

with open(generator.output_file, "w", encoding="utf-8") as f:
    f.write(text)
```

For an imperfect maze:

```python
from amazing import MazeGenerator

generator = MazeGenerator(
    width=20,
    height=12,
    entry=(0, 0),
    exit_=(19, 11),
    output_file="maze.txt",
    perfect=False,
    seed=42,
)

generator.generate()
text = generator.build_output_text()

with open(generator.output_file, "w", encoding="utf-8") as f:
    f.write(text)
```

---

# Summary

This project builds a reusable maze generator package that follows the subject requirements.

### Main points

- the maze is stored using hexadecimal wall encoding
- DFS is used to carve the main maze
- BFS is used to find one shortest solution
- the `42` pattern is kept using blocked fully closed cells
- imperfect mode adds loops by opening extra walls
- forbidden open `3x3` areas are avoided
- connectivity is checked to keep the maze valid
- the final output is generated in the required format

```text
This document is written by Saeedeh Asheri
```

# 👥 Team and Project Management

## Roles
The project was divided into two main areas to ensure a clean separation of concerns:
* `sasheri` (Backend & Algorithms):** Responsible for the core logic, including the `MazeGenerator`, the DFS carving algorithm, the BFS solver, grid state management, and the `42` mask implementation.
* `vebastos` (Frontend & Infrastructure):** Responsible for the graphical engine using MLX, direct memory pixel rendering, UI/keyboard controls, configuration parsing (`config.txt`), and project automation (`Makefile`).

## Planning and Evolution
We anticipated that the graphical rendering and the maze generation algorithms would be the most complex partsTherefore, we decided to work in parallel:
1. First, we agreed on the API (how the generator would pass the grid to the visual engine).
2. The backend was developed as an isolated, reusable package (`mazegen`).
3. The frontend was developed using dummy data until the backend was ready.
4. Finally, we integrated both parts and refined the visual output.

## Tools Used
**Version Control:** Git & GitHub for collaboration.
**Environment:** Python `venv` to isolate dependencies.
**Linters/Checkers:** `flake8` for PEP 8 compliance and `mypy` for static type checking.
**Graphics:** `mlx` (MiniLibX) for rendering.

---

# 📚 Resources and AI Usage

## Resources
During the development of this project, we relied on several classic computer science resources:
* Python 3 official documentation (especially for bitwise operations and file handling).
* Graph Theory tutorials for understanding Depth-First Search (DFS) for maze generation and Breadth-First Search (BFS) for finding the shortest path.
* MiniLibX documentation and 42 student guides regarding direct memory image manipulation (`mlx_get_data_addr`).

## AI Usage
Following the 42 guidelines, AI (Google Gemini) was used as a learning assistant and pair-programming tool, rather than a code generator. Specifically, AI was used to:
1. **Understand Low-Level Concepts:** Explain how 1D memory arrays map to 2D screen coordinates and how bitwise shifts work for injecting ARGB colors into RAM.
2. **Code Documentation:** Help format and translate our understanding of the code into clean, PEP 257 compliant docstrings and comments to prepare for the evaluation defense.
3. **Makefile Setup:** Assist in writing a robust Makefile that correctly complies with the strict subject rules (install, run, debug, clean, fclean, re, lint) and handles virtual environments automatically.