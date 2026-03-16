*This project has been created as part of the 42 curriculum by sasheri, vebastos.*

# A-Maze-ing

## Description

A-Maze-ing is a Python project that generates a random maze from a configuration file, displays it visually, and writes the generated maze to an output file using a hexadecimal wall representation. The project supports both **perfect mazes** and **imperfect mazes**, preserves a visible **“42” pattern** inside the maze using fully closed cells, and computes one **shortest valid path** from the entry to the exit.

The project is split into two main parts:

- a **reusable maze generation module** that can be packaged and installed later,
- a **visual application** that reads the configuration, generates the maze, and displays it with user interactions.

The core reusable class is `MazeGenerator`, which handles generation, validation, connectivity checks, solving, and output formatting.

---

## Features

- Random maze generation with optional reproducibility through a seed
- Support for **perfect** and **imperfect** mazes
- Hexadecimal encoding of cell walls
- Visible **“42”** pattern made of fully closed cells
- Validation of entry, exit, dimensions, and consistency rules
- Shortest path computation from entry to exit
- Visual display with interactive controls
- Reusable Python package for future projects

---

## Instructions

### Requirements

- Python **3.10+**
- A virtual environment is recommended
- Project dependencies installed through the provided build/setup files
- MLX available if you want to use the graphical display

### Run the project

The program must be executed with a configuration file:

```bash
python3 a_maze_ing.py config.txt
```

According to the subject, `a_maze_ing.py` is the main program and the configuration file is the only argument.

### Using the Makefile

The project includes a `Makefile` to automate the common tasks required by the subject:

```bash
make install
make run
make debug
make lint
make clean
```

Optional strict checking:

```bash
make lint-strict
```

### What the main script does

The main script:

1. reads the configuration file,
2. validates and parses its values,
3. creates the maze,
4. writes the output file,
5. opens the visual display.

### Interactive controls

The application provides at least the following interactions:

- generate a new random maze,
- show or hide the shortest path,
- change wall colours.

Extra controls may also be available depending on the implementation.

---

## Configuration File

The configuration file must contain **one `KEY=VALUE` pair per line**.
Lines beginning with `#` are comments and must be ignored.

### Mandatory keys

| Key | Description | Example |
|---|---|---|
| `WIDTH` | Maze width in number of cells | `WIDTH=20` |
| `HEIGHT` | Maze height in number of cells | `HEIGHT=15` |
| `ENTRY` | Entry coordinates `(x,y)` | `ENTRY=0,0` |
| `EXIT` | Exit coordinates `(x,y)` | `EXIT=19,14` |
| `OUTPUT_FILE` | Output filename | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Whether the maze must be perfect | `PERFECT=True` |

### Optional keys

The subject allows adding useful extra keys. In this project, an optional seed can be used for reproducibility.

Example:

```text
SEED=42
```

### Example default configuration

```text
# Maze dimensions
WIDTH=20
HEIGHT=15

# Entry and exit coordinates
ENTRY=0,0
EXIT=19,14

# Output file
OUTPUT_FILE=maze.txt

# Perfect or imperfect maze
PERFECT=True

# Optional reproducibility seed
SEED=42
```

### Expected format rules

- Comments start with `#`
- Each non-comment line must follow `KEY=VALUE`
- Numeric fields must contain valid integers
- `ENTRY` and `EXIT` must use the format `x,y`
- `PERFECT` must be a valid boolean value

### Error handling

The program is expected to handle invalid configurations gracefully, including:

- missing mandatory keys,
- invalid `KEY=VALUE` syntax,
- letters instead of numbers,
- invalid boolean values,
- invalid coordinate format,
- impossible maze parameters.

---

## Maze Representation

Each maze cell is stored as **one hexadecimal digit** encoding the state of its four walls.

### Bit encoding

| Bit | Direction |
|---|---|
| `0` | North |
| `1` | East |
| `2` | South |
| `3` | West |

A closed wall is represented by bit value `1`, and an open wall by bit value `0`.

Examples:

- `F` (`1111` in binary): all four walls are closed
- `3` (`0011` in binary): north and east walls are closed
- `A` (`1010` in binary): east and west walls are closed

The maze is written row by row in hexadecimal form.

---

## Output File Format

The output file contains:

1. the maze grid in hexadecimal form,
2. one empty line,
3. the entry coordinates,
4. the exit coordinates,
5. the shortest valid path using `N`, `E`, `S`, `W`.

Example:

```text
951395139551795151151153
EABA6E1285C3412EA828212
C6A4816A454144A482B20A
9A833640A395344543AE0D2

1,1
19,14
SWSESWSSSSEEEEENEESEESSSEEEESSSEENNENEE
```

All lines must end with `\n`.

---

## Chosen Maze Generation Algorithm

The main maze generation algorithm used in this project is **Depth-First Search (DFS)** with backtracking, implemented iteratively.

### How it works

1. Start from the entry cell.
2. Mark the current cell as visited.
3. Randomly choose an unvisited valid neighbour.
4. Break the wall between the current cell and the chosen neighbour.
5. Move to that neighbour.
6. If no unvisited neighbour exists, backtrack using a stack.
7. Continue until all reachable valid cells have been processed.

Blocked cells belonging to the `42` pattern are excluded from carving.

### Why this algorithm was chosen

DFS was chosen because:

- it is simple and reliable,
- it is a classic maze generation algorithm,
- it naturally creates a **perfect maze** structure first,
- it works well with randomness,
- it is easy to implement and explain during evaluation.

For **imperfect mazes**, extra walls are opened afterward to create loops while still respecting the project constraints.

---

## Solving Algorithm

The shortest path is computed with **Breadth-First Search (BFS)**.

### Why BFS was chosen

BFS is the right choice here because the maze graph is unweighted. It guarantees one **shortest valid path** between the entry and exit.

The returned path is encoded using the required direction letters:

- `N`
- `E`
- `S`
- `W`

---

## The “42” Pattern

The maze must visually contain a **“42”** pattern.
In this project, the pattern is implemented using **fully closed blocked cells**.

That means:

- these cells are never carved by the generator,
- they are never used by the solver,
- they remain visible in the displayed maze.

If the maze is too small to contain the pattern, the project prints a message on the terminal, which is allowed by the subject.

---

## Reusable Module Documentation

A reusable module is provided as a Python package named `mazegen-*`, located at the root of the repository as a build artifact (`.tar.gz` or `.whl`).

### What part is reusable

The reusable part is the maze generator package centered around the class:

```python
MazeGenerator
```

This reusable module provides:

- maze generation,
- input validation,
- connectivity checks,
- shortest-path solving,
- output text generation,
- access to the internal generated maze structure.

### Why it is reusable

The maze logic is separated from the visual interface. This means the generator can later be:

- imported into another Python project,
- tested independently,
- reused with another interface,
- packaged and installed with `pip`.

### Basic example

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
solution = generator.solve()
text = generator.build_output_text()

print(solution)
print(text)
```

### Passing custom parameters

You can customize at least:

- `width`
- `height`
- `entry`
- `exit_`
- `output_file`
- `perfect`
- `seed`

### Accessing the generated data

After generation, the module gives access to:

- the maze structure,
- the generated hexadecimal representation,
- the computed solution path.

Typical usage includes methods such as:

```python
generator.generate()
hex_maze = generator.to_hex_string()
solution = generator.solve()
output_text = generator.build_output_text()
```

---

## Project Structure

```text
.
├── README.md
├── a_maze_ing.py
├── mazegen.tar.gz
├── config.txt
├── Makefile
├── pyproject.toml
├── src/
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

---

## Team and Project Management

### Roles of each team member

- **sasheri**: backend and algorithms — maze generation logic, DFS carving, BFS solver, grid consistency, `42` mask, validation, and output generation.
- **vebastos**: frontend and infrastructure — visual rendering with MLX, keyboard controls, configuration parsing, application integration, and automation through the `Makefile`.

### Anticipated planning and how it evolved

At the beginning, we expected the project to have two main difficult areas:

- the **maze generation logic**,
- the **visual rendering and interaction layer**.

Because of that, we planned the work in parallel:

1. define the interface between the generator and the display,
2. implement the reusable generator package,
3. implement the visual application using temporary test data,
4. integrate both parts,
5. refine the rendering, configuration parsing, and output format.

This plan worked well overall, but during integration we had to spend more time than expected aligning the generator output with the display layer and making the configuration and packaging flow cleaner.

### What worked well

- clear separation between backend and frontend,
- reusable package design,
- use of classical graph algorithms that are easy to test and explain,
- parallel work organization,
- configuration-driven execution.

### What could be improved

- more automated tests for edge cases,
- earlier full integration testing,
- more detailed user documentation for controls and package installation,
- additional validation scenarios for malformed configuration files.

### Specific tools used

- **Git / GitHub** for collaboration and version control,
- **Python `venv`** for isolated environments,
- **flake8** for style checking,
- **mypy** for static type checking,
- **MiniLibX (MLX)** for the graphical display,
- **Makefile** for project automation.

---

## Resources

### Classic references

- Python official documentation
- Documentation and tutorials about **Depth-First Search (DFS)**
- Documentation and tutorials about **Breadth-First Search (BFS)**
- Graph theory references on spanning trees and shortest paths
- MiniLibX documentation and 42 student resources

### How AI was used

AI was used as a **learning and support tool**, not as a replacement for understanding the code.

It was used for the following tasks:

- clarifying low-level concepts such as bitwise wall encoding and pixel memory access,
- helping explain graph algorithm ideas used in the project,
- improving wording and formatting of documentation,
- assisting with the organization of the `Makefile` and development workflow,
- supporting code comments and explanation drafts before peer review.

All AI-generated suggestions were reviewed, tested, and discussed by the team before being kept.

---

## Technical Choices

### Perfect and imperfect modes

The project first generates a perfect maze using DFS. If `PERFECT=False`, additional walls are opened to create loops while keeping the maze valid.

### Connectivity guarantees

The code checks that all reachable non-blocked cells remain connected.

### Prevention of invalid open areas

The project avoids creating a fully open `3x3` zone, in order to respect the subject rule that corridors cannot be wider than 2 cells.

### Reproducibility

When a seed is provided, the same configuration generates the same maze again, which is useful for testing and debugging.

---

## Summary

A-Maze-ing is a maze generator and visualizer written in Python. It follows the 42 subject requirements by:

- reading a configuration file,
- generating a valid maze,
- displaying it visually,
- writing the maze to a hexadecimal output file,
- computing a shortest path,
- keeping a visible `42` pattern,
- providing a reusable package for future projects.
