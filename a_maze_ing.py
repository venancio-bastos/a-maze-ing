import random
from mlx import Mlx

class MazeApp:
	def __init__(self, width, height, title):
		# Dimensions
		self.width = width
		self.height = height
		self.title = title

		# Mlx init and window creation
		self.mlx = Mlx()
		self.ptr = self.mlx.mlx_init()
		self.win = self.mlx.mlx_new_window(self.ptr, self.width, self.height, self.title)

		# Image creation for window
		self.img = self.mlx.mlx_new_image(self.ptr, self.width, self.height)
		self.data, self.bpp, self.size_line, self.endian = self.mlx.mlx_get_data_addr(self.img)
		self.bytes_per_pixel = self.bpp // 8
		self.palettes = [
			{"bg": 0x000000, "border": 0xFFFFFF, "ui": 0x1E1E1E, "text": 0xFFFFFF}, # Dark Mode
			{"bg": 0x1a2a3a, "border": 0x3498db, "ui": 0x2c3e50, "text": 0xecf0f1}, # Blue Night
			{"bg": 0x1b1b1b, "border": 0x2ecc71, "ui": 0x27ae60, "text": 0xffffff}, # Hacker Green
			{"bg": 0x2d132c, "border": 0xee4540, "ui": 0x801336, "text": 0xc72c41}  # Cyberpunk
		]
		self.current_palette = random.randrange(len(self.palettes))

	def change_color_scheme(self):
		self.current_palette = random.randint(0, len(self.palettes) - 1)
		self.draw_all()

	def put_pixel(self, x, y, color):
		if 0 <= x < self.width and 0 <= y < self.height:
			offset = (y * self.size_line) + (x * self.bytes_per_pixel)
			self.data[offset] = color & 0xFF
			self.data[offset + 1] = (color >> 8) & 0xFF
			self.data[offset + 2] = (color >> 16) & 0xFF
			self.data[offset + 3] = 255

	def draw_all(self):
		theme = self.palettes[self.current_palette]
		self.draw_rect(0, 0, self.width, self.height, theme["bg"])
		self.draw_borders(theme["border"])

	def draw_rect(self, start_x, start_y, rect_width, rect_height, color):
		for y in range(start_y, start_y + rect_height):
			for x in range(start_x, start_x + rect_width):
				self.put_pixel(x, y, color)
	
	def draw_borders(self, color):
		margin_w = int(self.width * 0.10)
		margin_e = int(self.width * 0.10)
		margin_n = int(self.height * 0.05)
		margin_s = int(self.height * 0.20)

		maze_x = margin_w
		maze_y = margin_n
		maze_w = self.width - margin_w - margin_e
		maze_h = self.height - margin_n - margin_s
		
		color = 0xFFFFFF
		thickness = 7

		self.draw_rect(maze_x, maze_y, maze_w, thickness, color)
		self.draw_rect(maze_x, maze_y + maze_h - thickness, maze_w, thickness, color)
		self.draw_rect(maze_x, maze_y, thickness, maze_h, color)
		self.draw_rect(maze_x + maze_w - thickness, maze_y, thickness, maze_h, color)
		
	
	def draw_ui_text(self):
		theme = self.palettes[self.current_palette]
		y_text = int(self.height * 0.92)
		menu_items = ["1: REGEN", "2: PATH", "3: COLOR", "4: QUIT"]
		spacing = self.width // (len(menu_items) + 1)
		for i, item in enumerate(menu_items):
			x_pos = spacing * (i + 1) - 30
			self.mlx.mlx_string_put(self.ptr, self.win, x_pos, y_text, theme["text"], item)

	def handle_key(self, keycode, params):
		if keycode in [65307, 113, 52]:
			self.mlx.mlx_loop_exit(self.ptr)
		# elif keycode == 49:
		# elif keycode == 50:
		elif keycode == 51:
			self.change_color_scheme()
		return 0

	def render_frame(self, params):
		self.mlx.mlx_put_image_to_window(self.ptr, self.win, self.img, 0, 0)
		self.draw_ui_text()
		return 0

	def run(self):
		self.draw_all()

		self.mlx.mlx_key_hook(self.win, self.handle_key, None)
		self.mlx.mlx_loop_hook(self.ptr, self.render_frame, None)
		self.mlx.mlx_loop(self.ptr)

def main():
	app = MazeApp(800, 600, "A-Maze-ing")
	app.run()

if __name__ == "__main__":
	main()