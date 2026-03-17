import random
from typing import Any, Dict, List, Tuple

from mlx import Mlx

from MazeGen import MazeGenerator


class MazeApp:
    """Manage the graphical window, rendering, and keyboard events."""

    def __init__(
        self,
        width: int,
        height: int,
        title: str,
        config: Dict[str, Any],
    ) -> None:
        """Initialize the window and the maze generator."""
        self.width: int = width
        self.height: int = height
        self.title: str = title

        self.maze_cols: int = config["WIDTH"]
        self.maze_rows: int = config["HEIGHT"]
        self.entry: Tuple[int, int] = config["ENTRY"]
        self.exit: Tuple[int, int] = config["EXIT"]
        self.output_file: str = config["OUTPUT_FILE"]
        self.perfect: bool = config["PERFECT"]
        self.seed: int | None = config.get("SEED")

        self.mlx: Mlx = Mlx()
        self.ptr: Any = self.mlx.mlx_init()
        self.win: Any = self.mlx.mlx_new_window(
            self.ptr,
            self.width,
            self.height,
            self.title,
        )

        self.img: Any = self.mlx.mlx_new_image(
            self.ptr, self.width, self.height
        )
        self.data, self.bpp, self.size_line, self.endian = (
            self.mlx.mlx_get_data_addr(self.img)
        )
        self.bytes_per_pixel: int = self.bpp // 8

        self.palettes: List[Dict[str, int]] = [
            {
                "bg": 0x000000,
                "border": 0xFFFFFF,
                "ui": 0x1E1E1E,
                "text": 0xFFFFFF,
                "path": 0xFFD700,
            },
            {
                "bg": 0x1A2A3A,
                "border": 0x3498DB,
                "ui": 0x2C3E50,
                "text": 0xECF0F1,
                "path": 0xF1C40F,
            },
            {
                "bg": 0x1B1B1B,
                "border": 0x2ECC71,
                "ui": 0x27AE60,
                "text": 0xFFFFFF,
                "path": 0xE74C3C,
            },
            {
                "bg": 0x2D132C,
                "border": 0xEE4540,
                "ui": 0x801336,
                "text": 0xC72C41,
                "path": 0x2ECC71,
            },
        ]
        self.current_palette: int = random.randrange(len(self.palettes))

        self.show_path: bool = False
        self.path_coords: List[Tuple[int, int]] = []

        self.generator: MazeGenerator = MazeGenerator(
            self.maze_cols,
            self.maze_rows,
            self.entry,
            self.exit,
            self.output_file,
            self.perfect,
            seed=self.seed,
        )
        self._generate_and_save()

    def _generate_and_save(self) -> None:
        """Generate the maze, compute the path coordinates, and save output."""
        self.generator.generate()

        try:
            with open(self.output_file, "w", encoding="utf-8") as file:
                file.write(self.generator.build_output_text())
        except OSError as exc:
            print(f"Warning: Could not save output file: {exc}")

        solution: str | None = self.generator.get_solution()
        self.path_coords = [self.entry]

        if solution:
            cx, cy = self.entry
            for move in solution:
                if move == "N":
                    cy -= 1
                elif move == "S":
                    cy += 1
                elif move == "E":
                    cx += 1
                elif move == "W":
                    cx -= 1
                self.path_coords.append((cx, cy))

    def put_pixel(self, x: int, y: int, color: int) -> None:
        """Write one pixel in the image buffer."""
        if 0 <= x < self.width and 0 <= y < self.height:
            offset: int = (y * self.size_line) + (x * self.bytes_per_pixel)
            self.data[offset] = color & 0xFF
            self.data[offset + 1] = (color >> 8) & 0xFF
            self.data[offset + 2] = (color >> 16) & 0xFF
            self.data[offset + 3] = 255

    def fill_area(
        self,
        start_x: int,
        start_y: int,
        rect_width: int,
        rect_height: int,
        color: int,
    ) -> None:
        """Draw a filled rectangle."""
        for y in range(start_y, start_y + rect_height):
            for x in range(start_x, start_x + rect_width):
                self.put_pixel(x, y, color)

    def draw_maze(self, wall_color: int) -> None:
        """Render the maze walls."""
        margin_w: int = int(self.width * 0.10)
        margin_s: int = int(self.height * 0.20)
        margin_n: int = int(self.height * 0.05)

        maze_x: int = margin_w
        maze_y: int = margin_n
        maze_w: int = self.width - (margin_w * 2)
        maze_h: int = self.height - margin_n - margin_s

        cell_w: int = maze_w // self.maze_cols
        cell_h: int = maze_h // self.maze_rows
        thickness: int = 2

        grid: List[List[int]] = self.generator.get_grid()
        blocked_mask: List[List[bool]] = self.generator.get_blocked_mask()

        for y in range(self.maze_rows):
            for x in range(self.maze_cols):
                cell_val: int = grid[y][x]
                is_blocked: bool = blocked_mask[y][x]
                px: int = maze_x + (x * cell_w)
                py: int = maze_y + (y * cell_h)

                if is_blocked:
                    self.fill_area(px, py, cell_w, cell_h, wall_color)
                else:
                    if cell_val & 1:
                        self.fill_area(px, py, cell_w, thickness, wall_color)
                    if cell_val & 2:
                        self.fill_area(
                            px + cell_w - thickness,
                            py,
                            thickness,
                            cell_h,
                            wall_color,
                        )
                    if cell_val & 4:
                        self.fill_area(
                            px,
                            py + cell_h - thickness,
                            cell_w,
                            thickness,
                            wall_color,
                        )
                    if cell_val & 8:
                        self.fill_area(px, py, thickness, cell_h, wall_color)

    def draw_path(self, color: int) -> None:
        """Draw the shortest path on top of the maze."""
        if not self.path_coords:
            return

        margin_w: int = int(self.width * 0.10)
        margin_s: int = int(self.height * 0.20)
        margin_n: int = int(self.height * 0.05)

        maze_w: int = self.width - (margin_w * 2)
        maze_h: int = self.height - margin_n - margin_s

        cell_w: int = maze_w // self.maze_cols
        cell_h: int = maze_h // self.maze_rows

        for x, y in self.path_coords:
            px: int = margin_w + (x * cell_w) + (cell_w // 4)
            py: int = margin_n + (y * cell_h) + (cell_h // 4)
            pw: int = cell_w // 2
            ph: int = cell_h // 2
            self.fill_area(px, py, pw, ph, color)

    def draw_endpoints(self) -> None:
        """Draw the entry and exit markers."""
        margin_w: int = int(self.width * 0.10)
        margin_s: int = int(self.height * 0.20)
        margin_n: int = int(self.height * 0.05)

        maze_w: int = self.width - (margin_w * 2)
        maze_h: int = self.height - margin_n - margin_s

        cell_w: int = maze_w // self.maze_cols
        cell_h: int = maze_h // self.maze_rows

        ex, ey = self.entry
        px_entry: int = margin_w + (ex * cell_w) + (cell_w // 4)
        py_entry: int = margin_n + (ey * cell_h) + (cell_h // 4)
        self.fill_area(px_entry, py_entry, cell_w // 2, cell_h // 2, 0x00FF00)

        xx, xy = self.exit
        px_exit: int = margin_w + (xx * cell_w) + (cell_w // 4)
        py_exit: int = margin_n + (xy * cell_h) + (cell_h // 4)
        self.fill_area(px_exit, py_exit, cell_w // 2, cell_h // 2, 0xFF0000)

    def draw_ui_text(self) -> None:
        """Render the bottom menu."""
        theme: Dict[str, int] = self.palettes[self.current_palette]
        y_text: int = int(self.height * 0.92)
        menu_items: List[str] = ["1: REGEN", "2: PATH", "3: COLOR", "4: QUIT"]
        spacing: int = self.width // (len(menu_items) + 1)

        for index, item in enumerate(menu_items):
            x_pos: int = spacing * (index + 1) - 30
            self.mlx.mlx_string_put(
                self.ptr,
                self.win,
                x_pos,
                y_text,
                theme["text"],
                item,
            )

    def change_color_scheme(self) -> None:
        """Change the active palette and redraw the maze."""
        self.current_palette = random.randint(0, len(self.palettes) - 1)
        self.draw_all()

    def draw_all(self) -> None:
        """Draw the full scene."""
        theme: Dict[str, int] = self.palettes[self.current_palette]
        self.fill_area(0, 0, self.width, self.height, theme["bg"])
        self.draw_maze(theme["border"])

        if self.show_path:
            self.draw_path(theme["path"])

        self.draw_endpoints()

    def handle_key(self, keycode: int, _params: Any) -> int:
        """Handle user keyboard interactions."""
        if keycode in [65307, 113, 52]:
            self.mlx.mlx_loop_exit(self.ptr)
        elif keycode == 49:
            self.generator = MazeGenerator(
                self.maze_cols,
                self.maze_rows,
                self.entry,
                self.exit,
                self.output_file,
                self.perfect,
                seed=self.seed,
            )
            self._generate_and_save()
            self.draw_all()
        elif keycode == 50:
            self.show_path = not self.show_path
            self.draw_all()
        elif keycode == 51:
            self.change_color_scheme()
        return 0

    def render_frame(self, _params: Any) -> int:
        """Push the image buffer to the window."""
        self.mlx.mlx_put_image_to_window(self.ptr, self.win, self.img, 0, 0)
        self.draw_ui_text()
        return 0

    def run(self) -> None:
        """Start the graphical event loop."""
        self.draw_all()
        self.mlx.mlx_key_hook(self.win, self.handle_key, None)
        self.mlx.mlx_loop_hook(self.ptr, self.render_frame, None)
        self.mlx.mlx_loop(self.ptr)
