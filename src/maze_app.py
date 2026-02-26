import random
from typing import Any, List, Dict
from mlx import Mlx
from generator import MazeGenerator

class MazeApp:
	"""
	Responsible for managing window, graphical rendering and keyboard events.
	"""
	def __init__(self, width: int, height: int, title: str, maze_cols: int, maze_rows: int) -> None:
		"""
		Initializes the graphical app, memory variables.
		"""
		# Window dimensions and grid size
		self.width = width
		self.height = height
		self.title = title
		self.maze_cols = maze_cols
		self.maze_rows = maze_rows

		# Mlx init and window creation
		self.mlx = Mlx()
		self.ptr = self.mlx.mlx_init()
		self.win = self.mlx.mlx_new_window(self.ptr, self.width, self.height, self.title)

		# Image creation for window
		self.img = self.mlx.mlx_new_image(self.ptr, self.width, self.height)
		self.data, self.bpp, self.size_line, self.endian = self.mlx.mlx_get_data_addr(self.img)
		self.bytes_per_pixel = self.bpp // 8

		# Color palettes ( Background, Walls, UI Panel, Text)
		self.palettes = [
			{"bg": 0x000000, "border": 0xFFFFFF, "ui": 0x1E1E1E, "text": 0xFFFFFF},
			{"bg": 0x1a2a3a, "border": 0x3498db, "ui": 0x2c3e50, "text": 0xecf0f1},
			{"bg": 0x1b1b1b, "border": 0x2ecc71, "ui": 0x27ae60, "text": 0xffffff},
			{"bg": 0x2d132c, "border": 0xee4540, "ui": 0x801336, "text": 0xc72c41}
		]
		self.current_palette = random.randrange(len(self.palettes))

		# Creation of initial maze
		self.generator = MazeGenerator(self.maze_cols, self.maze_rows)
		self.generator.generate(0, 0)

	def put_pixel(self, x: int, y: int, color: int) -> None:
		"""
		Puts a single pixel in the image memory if it's within screen boundaries.
		"""
		if 0 <= x < self.width and 0 <= y < self.height:
			offset = (y * self.size_line) + (x * self.bytes_per_pixel)
			self.data[offset] = color & 0xFF
			self.data[offset + 1] = (color >> 8) & 0xFF
			self.data[offset + 2] = (color >> 16) & 0xFF
			self.data[offset + 3] = 255

	def draw_rect(self, start_x: int, start_y: int, rect_width: int, rect_height: int, color: int) -> None:
		"""
		Draws a filled rectangle in the image memory, pixel by pixel.
		"""
		for y in range(start_y, start_y + rect_height):
			for x in range(start_x, start_x + rect_width):
				self.put_pixel(x, y, color)
	
	def draw_maze(self, wall_color: int) -> None:
		"""
		Calculates dynamic margins, cell sizes, and draws walls based 
		on the generator's bitwise grid representation (1, 2, 4, 8).
		"""
		margin_w = int(self.width * 0.10)
		margin_s = int(self.height * 0.20)
		margin_n = int(self.height * 0.05)

		maze_x = margin_w
		maze_y = margin_n
		maze_w = self.width - (margin_w * 2)
		maze_h = self.height - margin_n - margin_s

		cell_w = maze_w // self.maze_cols
		cell_h = maze_h // self.maze_rows
		thickness = 2
		
		grid = self.generator.grid

		for y in range(self.maze_rows):
			for x in range(self.maze_cols):
				cell_val = grid[y][x]

				px = maze_x + (x * cell_w)
				py = maze_y + (y * cell_h)

				if cell_val & 1:
					self.draw_rect(px, py, cell_w, thickness, wall_color)
				if cell_val & 2:
					self.draw_rect(px + cell_w - thickness, py, thickness, cell_h, wall_color)
				if cell_val & 4:
					self.draw_rect(px, py + cell_h - thickness, cell_w, thickness, wall_color)
				if cell_val & 8:
					self.draw_rect(px, py, thickness, cell_h, wall_color)
	
	def draw_ui_text(self) -> None:
		"""
		Draws the menu text.
		"""
		theme = self.palettes[self.current_palette]
		y_text = int(self.height * 0.92)
		menu_items = ["1: REGEN", "2: PATH", "3: COLOR", "4: QUIT"]
		spacing = self.width // (len(menu_items) + 1)
		for i, item in enumerate(menu_items):
			x_pos = spacing * (i + 1) - 30
			self.mlx.mlx_string_put(self.ptr, self.win, x_pos, y_text, theme["text"], item)

	def change_color_scheme(self) -> None:
		"""
		Switches to a random palette and triggers a full redraw.
		"""
		self.current_palette = random.randint(0, len(self.palettes) - 1)
		self.draw_all()

	def draw_all(self) -> None:
		"""
		Redraws the maze and UI panel.
		"""
		theme = self.palettes[self.current_palette]
		self.draw_rect(0, 0, self.width, self.height, theme["bg"])
		self.draw_maze(theme["border"])

	def handle_key(self, keycode: int, params: Any) -> int:
		"""
		Hook that reacts to keys pressed by the user.
		"""
		if keycode in [65307, 113, 52]:
			self.mlx.mlx_loop_exit(self.ptr)
		# elif keycode == 49:
		# elif keycode == 50:
		elif keycode == 51:
			self.change_color_scheme()
		return 0

	def render_frame(self, params: Any) -> int:
		"""
		Continuously pushes the image buffer to the window and draws the UI text.
		"""
		self.mlx.mlx_put_image_to_window(self.ptr, self.win, self.img, 0, 0)
		self.draw_ui_text()
		return 0

	def run(self) -> None:
		"""
		Prepares the initial screen and launches the MLX infinite loop.
		"""
		self.draw_all()
		self.mlx.mlx_key_hook(self.win, self.handle_key, None)
		self.mlx.mlx_loop_hook(self.ptr, self.render_frame, None)
		self.mlx.mlx_loop(self.ptr)