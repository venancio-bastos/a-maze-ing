import random
from typing import Any, List, Dict, Tuple
from mlx import Mlx
from src.MazeGen import MazeGenerator


class MazeApp:
    """
    Responsible for managing window, graphical rendering and keyboard events.
    """
    def __init__(
            self,
            width: int,
            height: int,
            title: str,
            config: Dict[str, Any]
            ) -> None:
        """
        Initializes the graphical app, memory variables and the maze generator.
        """
        self.width: int = width
        self.height: int = height
        self.title: str = title

        self.maze_cols: int = config['WIDTH']
        self.maze_rows: int = config['HEIGHT']
        self.entry: Tuple[int, int] = config['ENTRY']
        self.exit: Tuple[int, int] = config['EXIT']
        self.output_file: str = config['OUTPUT_FILE']
        self.perfect: bool = config['PERFECT']

        self.mlx: Mlx = Mlx()
        self.ptr: Any = self.mlx.mlx_init()
        self.win: Any = self.mlx.mlx_new_window(
            self.ptr,
            self.width,
            self.height,
            self.title
        )

        # Creates invisible screen in ram to draw
        self.img: Any = self.mlx.mlx_new_image(
            self.ptr, self.width, self.height
        )
        # Ask the adress of the window in ram
        (
            self.data,  # Adress of first pixel
            self.bpp,  # Bits per pixel ( 32 bits for ARGB)
            self.size_line,  # Number of horizontal bites per line
            self.endian  # How processor reads info
        ) = self.mlx.mlx_get_data_addr(self.img)

        #  1 byte = 8 bits so 32 // 8 gives the amount of bits
        # each pixel have ( 4 )
        self.bytes_per_pixel: int = self.bpp // 8

        self.palettes: List[Dict[str, int]] = [
            {
                "bg": 0x000000,
                "border": 0xFFFFFF,
                "ui": 0x1E1E1E,
                "text": 0xFFFFFF,
                "path": 0xFFD700
            },
            {
                "bg": 0x1a2a3a,
                "border": 0x3498db,
                "ui": 0x2c3e50,
                "text": 0xecf0f1,
                "path": 0xf1c40f
            },
            {
                "bg": 0x1b1b1b,
                "border": 0x2ecc71,
                "ui": 0x27ae60,
                "text": 0xffffff,
                "path": 0xe74c3c
            },
            {
                "bg": 0x2d132c,
                "border": 0xee4540,
                "ui": 0x801336,
                "text": 0xc72c41,
                "path": 0x2ecc71
            }
        ]
        self.current_palette: int = random.randrange(len(self.palettes))

        # UI States
        self.show_path: bool = False
        self.path_coords: List[Tuple[int, int]] = []

        # Create generator and run the initial setup
        self.generator: MazeGenerator = MazeGenerator(
            self.maze_cols,
            self.maze_rows,
            self.entry,
            self.exit,
            self.output_file,
            self.perfect
        )
        self._generate_and_save()

    def _generate_and_save(self) -> None:
        """
        Generates the maze, updates the path coordinates,
        and saves the output file.
        """
        # 1. Ask the backend algorithm to create the mathematical grid
        self.generator.generate()

        # 2. Save the required output file for the 42 subject evaluation
        try:
            with open(self.output_file, 'w') as f:
                # build_output_text() returns the raw hex grid
                # and the solution path
                f.write(self.generator.build_output_text())
        except Exception as e:
            print(f"Warning: Could not save output file: {e}")

        # 3. Translate the string of letters (e.g., "NNESW")
        # into a list of (x, y) coordinates.
        # Why? Because the graphical engine doesn't understand "North";
        # it only understands "draw a square at x=5, y=3".
        solution: str | None = self.generator.get_solution()

        # Start the path list with the entry coordinate (e.g., [0, 0])
        self.path_coords = [self.entry]

        if solution:
            # cx and cy represent our "Current X" and "Current Y" on the grid
            cx, cy = self.entry
            for move in solution:
                # Grid Y grows downwards.
                # So moving North means Y decreases (-1)
                if move == 'N':
                    cy -= 1
                elif move == 'S':
                    cy += 1
                elif move == 'E':
                    cx += 1
                elif move == 'W':
                    cx -= 1
                # Save the new coordinate to our path list
                self.path_coords.append((cx, cy))

    def put_pixel(self, x: int, y: int, color: int) -> None:
        """
        Injects a single pixel's color directly into the computer's RAM.
        """
        # Safety check: If we try to draw outside the window (e.g., x = -5),
        # the program will crash with a Segmentation Fault. This prevents that.
        if 0 <= x < self.width and 0 <= y < self.height:
            # RAM is a 1D straight line of memory bytes.
            # To find a 2D pixel (x,y), we skip 'y' full lines of bytes,
            # and then skip 'x' pixels forward (each pixel is 4 bytes).
            offset: int = (y * self.size_line) + (x * self.bytes_per_pixel)

            # The 'color' is a 32-bit integer (e.g., 0xAARRGGBB).
            # RAM expects 1 byte per memory slot. We use Bitwise operations:
            # & 0xFF keeps only the last 8 bits (1 byte).
            # >> 8 shifts the bits to the right to expose the Green channel.
            # >> 16 shifts the bits to expose the Red channel.
            self.data[offset] = color & 0xFF              # Blue channel
            self.data[offset + 1] = (color >> 8) & 0xFF   # Green channel
            self.data[offset + 2] = (color >> 16) & 0xFF  # Red channel
            self.data[offset + 3] = 255  # Alpha (255 = fully opaque)

    def fill_area(
            self,
            start_x: int,
            start_y: int,
            rect_width: int,
            rect_height: int,
            color: int
            ) -> None:
        """
        Draws a solid block by acting like a printer, painting row by row.
        """
        # The outer loop goes top to bottom (Y axis)
        for y in range(start_y, start_y + rect_height):
            # The inner loop goes left to right (X axis)
            for x in range(start_x, start_x + rect_width):
                self.put_pixel(x, y, color)

    def draw_maze(self, wall_color: int) -> None:
        """
        Translates the mathematical grid into physical walls on the screen.
        """
        # 1. Calculate screen margins so the maze
        # doesn't touch the window borders
        # 10% empty space on Left/Right
        margin_w: int = int(self.width * 0.10)
        # 20% empty space on Bottom (for UI)
        margin_s: int = int(self.height * 0.20)
        # 5% empty space on Top
        margin_n: int = int(self.height * 0.05)

        # 2. Define the actual starting point and size
        # of the drawable maze area
        maze_x: int = margin_w
        maze_y: int = margin_n
        maze_w: int = self.width - (margin_w * 2)
        maze_h: int = self.height - margin_n - margin_s

        # 3. Calculate how big each grid cell should be in physical pixels
        cell_w: int = maze_w // self.maze_cols
        cell_h: int = maze_h // self.maze_rows
        thickness: int = 2  # The physical width of the walls in pixels

        # Fetch the logic data
        grid: List[List[int]] = self.generator.get_grid()
        blocked_mask: List[List[bool]] = self.generator.get_blocked_mask()

        # Loop through every single cell in the grid
        for y in range(self.maze_rows):
            for x in range(self.maze_cols):
                cell_val: int = grid[y][x]
                is_blocked: bool = blocked_mask[y][x]

                # px and py are the exact screen pixel coordinates
                # where this cell begins
                px: int = maze_x + (x * cell_w)
                py: int = maze_y + (y * cell_h)

                if is_blocked:
                    # If this cell is part of the giant '42',
                    # fill the entire cell solid
                    self.fill_area(px, py, cell_w, cell_h, wall_color)
                else:
                    # Bitwise checks (&).
                    # The generator encoded walls as numbers:
                    # 1 = North, 2 = East, 4 = South, 8 = West.
                    # Has North Wall?
                    if cell_val & 1:
                        self.fill_area(px, py, cell_w, thickness, wall_color)
                    #  Has East Wall? (Drawn on the right edge)
                    if cell_val & 2:
                        self.fill_area(
                            px + cell_w - thickness, py,
                            thickness, cell_h, wall_color
                        )
                    # Has South Wall? (Drawn on the bottom edge)
                    if cell_val & 4:
                        self.fill_area(
                            px, py + cell_h - thickness,
                            cell_w, thickness, wall_color
                        )
                    # Has West Wall?
                    if cell_val & 8:
                        self.fill_area(px, py, thickness, cell_h, wall_color)

    def draw_path(self, color: int) -> None:
        """
        Draws the solved path as small colored blocks inside the maze paths.
        """
        # If there is no solution, don't draw anything
        if not self.path_coords:
            return

        # Recalculate margins and cell sizes (same math as draw_maze)
        margin_w: int = int(self.width * 0.10)
        margin_s: int = int(self.height * 0.20)
        margin_n: int = int(self.height * 0.05)

        maze_w: int = self.width - (margin_w * 2)
        maze_h: int = self.height - margin_n - margin_s

        cell_w: int = maze_w // self.maze_cols
        cell_h: int = maze_h // self.maze_rows

        for (x, y) in self.path_coords:
            # We add (cell_w // 4) to push the drawing to
            # the CENTER of the cell.
            px: int = margin_w + (x * cell_w) + (cell_w // 4)
            py: int = margin_n + (y * cell_h) + (cell_h // 4)

            # The path block size is half the size of the cell (cell_w // 2)
            pw: int = cell_w // 2
            ph: int = cell_h // 2
            self.fill_area(px, py, pw, ph, color)

    def draw_endpoints(self) -> None:
        """
        Draws the entry (Green) and exit (Red) points
        so they are clearly visible.
        """
        # Recalculate margins and cell sizes
        margin_w: int = int(self.width * 0.10)
        margin_s: int = int(self.height * 0.20)
        margin_n: int = int(self.height * 0.05)

        maze_w: int = self.width - (margin_w * 2)
        maze_h: int = self.height - margin_n - margin_s

        cell_w: int = maze_w // self.maze_cols
        cell_h: int = maze_h // self.maze_rows

        # Draw Entry Block in Green (Hex color: 0x00FF00)
        ex, ey = self.entry
        px_entry: int = margin_w + (ex * cell_w) + (cell_w // 4)
        py_entry: int = margin_n + (ey * cell_h) + (cell_h // 4)
        self.fill_area(px_entry, py_entry, cell_w // 2, cell_h // 2, 0x00FF00)

        # Draw Exit Block in Red (Hex color: 0xFF0000)
        xx, xy = self.exit
        px_exit: int = margin_w + (xx * cell_w) + (cell_w // 4)
        py_exit: int = margin_n + (xy * cell_h) + (cell_h // 4)
        self.fill_area(px_exit, py_exit, cell_w // 2, cell_h // 2, 0xFF0000)

    def draw_ui_text(self) -> None:
        """
        Renders the bottom menu options.
        """
        theme: Dict[str, int] = self.palettes[self.current_palette]

        # y_text is placed at 92% of the window height (near the bottom)
        y_text: int = int(self.height * 0.92)
        menu_items: List[str] = ["1: REGEN", "2: PATH", "3: COLOR", "4: QUIT"]

        # Calculate equal spacing to distribute
        # the text evenly across the width
        spacing: int = self.width // (len(menu_items) + 1)
        for i, item in enumerate(menu_items):
            x_pos: int = spacing * (i + 1) - 30
            # Ask MLX engine to write the string at the specified coordinates
            self.mlx.mlx_string_put(
                self.ptr, self.win, x_pos, y_text, theme["text"], item
            )

    def change_color_scheme(self) -> None:
        """Selects a random palette index and forces a full screen redraw."""
        self.current_palette = random.randint(0, len(self.palettes) - 1)
        self.draw_all()

    def draw_all(self) -> None:
        """
        The master rendering function. It draws everything back-to-front
        (Painter's Algorithm).
        """
        theme: Dict[str, int] = self.palettes[self.current_palette]

        # 1. Clear the entire screen by drawing a giant background rectangle
        self.fill_area(0, 0, self.width, self.height, theme["bg"])
        # 2. Draw the maze walls on top
        self.draw_maze(theme["border"])

        # 3. Draw the path if the user pressed '2'
        if self.show_path:
            self.draw_path(theme["path"])
            self.draw_endpoints()

    def handle_key(self, keycode: int, params: Any) -> int:
        """
        Intercepts keyboard presses. Keycodes represent physical keys.
        """
        if keycode in [65307, 113, 52]:  # Keys: Esc, 'Q', '4'
            self.mlx.mlx_loop_exit(self.ptr)  # Safely breaks the infinite loop
        elif keycode == 49:  # Key: '1' (REGEN)
            # Delete old maze, create a new one, and redraw
            self.generator = MazeGenerator(
                self.maze_cols, self.maze_rows, self.entry,
                self.exit, self.output_file, self.perfect
            )
            self._generate_and_save()
            self.draw_all()
        elif keycode == 50:  # Key: '2' (PATH)
            # Toggle boolean True/False and redraw
            self.show_path = not self.show_path
            self.draw_all()
        elif keycode == 51:  # Key: '3' (COLOR)
            self.change_color_scheme()
        return 0

    def render_frame(self, params: Any) -> int:
        """
        Continuously takes the image built in RAM and pushes it to the display.
        """
        self.mlx.mlx_put_image_to_window(self.ptr, self.win, self.img, 0, 0)
        self.draw_ui_text()
        return 0

    def run(self) -> None:
        """
        Prepares the first frame and hands over program control to MLX.
        """
        self.draw_all()
        # Tell MLX to run handle_key whenever a key is pressed
        self.mlx.mlx_key_hook(self.win, self.handle_key, None)
        # Tell MLX to run render_frame constantly
        self.mlx.mlx_loop_hook(self.ptr, self.render_frame, None)

        # Start the infinite graphical loop.
        # The script essentially freezes here.
        self.mlx.mlx_loop(self.ptr)
