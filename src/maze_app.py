import random
from typing import Any, List, Dict, Tuple
from mlx import Mlx
from mazegen import MazeGenerator

class MazeApp:
    """
    Responsible for managing window, graphical rendering and keyboard events.
    """
    def __init__(self, width: int, height: int, title: str, config: Dict[str, Any]) -> None:
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
        self.win: Any = self.mlx.mlx_new_window(self.ptr, self.width, self.height, self.title)

        self.img: Any = self.mlx.mlx_new_image(self.ptr, self.width, self.height)
        self.data, self.bpp, self.size_line, self.endian = self.mlx.mlx_get_data_addr(self.img)
        self.bytes_per_pixel: int = self.bpp // 8

        self.palettes: List[Dict[str, int]] = [
            {"bg": 0x000000, "border": 0xFFFFFF, "ui": 0x1E1E1E, "text": 0xFFFFFF, "path": 0xFFD700},
            {"bg": 0x1a2a3a, "border": 0x3498db, "ui": 0x2c3e50, "text": 0xecf0f1, "path": 0xf1c40f},
            {"bg": 0x1b1b1b, "border": 0x2ecc71, "ui": 0x27ae60, "text": 0xffffff, "path": 0xe74c3c},
            {"bg": 0x2d132c, "border": 0xee4540, "ui": 0x801336, "text": 0xc72c41, "path": 0x2ecc71}
        ]
        self.current_palette: int = random.randrange(len(self.palettes))
        
        # UI States
        self.show_path: bool = False
        self.path_coords: List[Tuple[int, int]] = []

        # Create generator and run the initial setup
        self.generator: MazeGenerator = MazeGenerator(
            self.maze_cols, self.maze_rows, self.entry, self.exit, self.output_file, self.perfect
        )
        self._generate_and_save()

    def _generate_and_save(self) -> None:
        """
        Generates the maze, updates the path coordinates, and saves the output file.
        """
        self.generator.generate()
        
        # Save output file required by 42
        try:
            with open(self.output_file, 'w') as f:
                f.write(self.generator.build_output_text())
        except Exception as e:
            print(f"Warning: Could not save output file: {e}")

        # Translate the string of letters (N, S, E, W) into (x, y) coordinates for drawing
        solution: str | None = self.generator.get_solution()
        self.path_coords = [self.entry]
        if solution:
            cx, cy = self.entry
            for move in solution:
                if move == 'N': cy -= 1
                elif move == 'S': cy += 1
                elif move == 'E': cx += 1
                elif move == 'W': cx -= 1
                self.path_coords.append((cx, cy))

    def put_pixel(self, x: int, y: int, color: int) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            offset: int = (y * self.size_line) + (x * self.bytes_per_pixel)
            self.data[offset] = color & 0xFF
            self.data[offset + 1] = (color >> 8) & 0xFF
            self.data[offset + 2] = (color >> 16) & 0xFF
            self.data[offset + 3] = 255

    def draw_rect(self, start_x: int, start_y: int, rect_width: int, rect_height: int, color: int) -> None:
        for y in range(start_y, start_y + rect_height):
            for x in range(start_x, start_x + rect_width):
                self.put_pixel(x, y, color)
    
    def draw_maze(self, wall_color: int) -> None:
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
        
        # NOW USING THE OFFICIAL GETTERS!
        grid: List[List[int]] = self.generator.get_grid()
        blocked_mask: List[List[bool]] = self.generator.get_blocked_mask()

        for y in range(self.maze_rows):
            for x in range(self.maze_cols):
                cell_val: int = grid[y][x]
                is_blocked: bool = blocked_mask[y][x]

                px: int = maze_x + (x * cell_w)
                py: int = maze_y + (y * cell_h)

                if is_blocked:
                    self.draw_rect(px, py, cell_w, cell_h, wall_color)
                else:
                    if cell_val & 1:
                        self.draw_rect(px, py, cell_w, thickness, wall_color)
                    if cell_val & 2:
                        self.draw_rect(px + cell_w - thickness, py, thickness, cell_h, wall_color)
                    if cell_val & 4:
                        self.draw_rect(px, py + cell_h - thickness, cell_w, thickness, wall_color)
                    if cell_val & 8:
                        self.draw_rect(px, py, thickness, cell_h, wall_color)

    def draw_path(self, color: int) -> None:
        """
        Draws the solved path as small blocks inside the maze paths.
        """
        if not self.path_coords:
            return
            
        margin_w: int = int(self.width * 0.10)
        margin_s: int = int(self.height * 0.20)
        margin_n: int = int(self.height * 0.05)

        maze_w: int = self.width - (margin_w * 2)
        maze_h: int = self.height - margin_n - margin_s

        cell_w: int = maze_w // self.maze_cols
        cell_h: int = maze_h // self.maze_rows
        
        for (x, y) in self.path_coords:
            px: int = margin_w + (x * cell_w) + (cell_w // 4)
            py: int = margin_n + (y * cell_h) + (cell_h // 4)
            pw: int = cell_w // 2
            ph: int = cell_h // 2
            self.draw_rect(px, py, pw, ph, color)
    
    def draw_endpoints(self) -> None:
        """
        Draws the entry (Green) and exit (Red) points so they are clearly visible.
        """
        margin_w: int = int(self.width * 0.10)
        margin_s: int = int(self.height * 0.20)
        margin_n: int = int(self.height * 0.05)

        maze_w: int = self.width - (margin_w * 2)
        maze_h: int = self.height - margin_n - margin_s

        cell_w: int = maze_w // self.maze_cols
        cell_h: int = maze_h // self.maze_rows
        
        # Draw Entry (Green)
        ex, ey = self.entry
        px_entry: int = margin_w + (ex * cell_w) + (cell_w // 4)
        py_entry: int = margin_n + (ey * cell_h) + (cell_h // 4)
        self.draw_rect(px_entry, py_entry, cell_w // 2, cell_h // 2, 0x00FF00)

        # Draw Exit (Red)
        xx, xy = self.exit
        px_exit: int = margin_w + (xx * cell_w) + (cell_w // 4)
        py_exit: int = margin_n + (xy * cell_h) + (cell_h // 4)
        self.draw_rect(px_exit, py_exit, cell_w // 2, cell_h // 2, 0xFF0000)

    def draw_ui_text(self) -> None:
        theme: Dict[str, int] = self.palettes[self.current_palette]
        y_text: int = int(self.height * 0.92)
        menu_items: List[str] = ["1: REGEN", "2: PATH", "3: COLOR", "4: QUIT"]
        spacing: int = self.width // (len(menu_items) + 1)
        for i, item in enumerate(menu_items):
            x_pos: int = spacing * (i + 1) - 30
            self.mlx.mlx_string_put(self.ptr, self.win, x_pos, y_text, theme["text"], item)

    def change_color_scheme(self) -> None:
        self.current_palette = random.randint(0, len(self.palettes) - 1)
        self.draw_all()

    def draw_all(self) -> None:
        theme: Dict[str, int] = self.palettes[self.current_palette]
        self.draw_rect(0, 0, self.width, self.height, theme["bg"])
        self.draw_maze(theme["border"])
        
        if self.show_path:
            self.draw_path(theme["path"])
            self.draw_endpoints()

    def handle_key(self, keycode: int, params: Any) -> int:
        if keycode in [65307, 113, 52]: # Esc, Q, 4
            self.mlx.mlx_loop_exit(self.ptr)
        elif keycode == 49: # 1: REGEN
            self.generator = MazeGenerator(
                self.maze_cols, self.maze_rows, self.entry, self.exit, self.output_file, self.perfect
            )
            self._generate_and_save()
            self.draw_all()
        elif keycode == 50: # 2: PATH
            self.show_path = not self.show_path
            self.draw_all()
        elif keycode == 51: # 3: COLOR
            self.change_color_scheme()
        return 0

    def render_frame(self, params: Any) -> int:
        self.mlx.mlx_put_image_to_window(self.ptr, self.win, self.img, 0, 0)
        self.draw_ui_text()
        return 0

    def run(self) -> None:
        self.draw_all()
        self.mlx.mlx_key_hook(self.win, self.handle_key, None)
        self.mlx.mlx_loop_hook(self.ptr, self.render_frame, None)
        self.mlx.mlx_loop(self.ptr)