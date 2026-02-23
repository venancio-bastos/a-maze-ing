import sys
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

	def put_pixel(self, x, y, color):
		if 0 <= x < self.width and 0 <= y < self.height:
			offset = (y * self.size_line) + (x * self.bytes_per_pixel)

		self.data[offset] = color & 0xFF
		self.data[offset + 1] = (color >> 8) & 0xFF
		self.data[offset + 2] = (color >> 16) & 0xFF
		self.data[offset + 3] = 255

	def draw_rect(self, start_x, start_y, rect_width, rect_height, color):
		for y in range(start_y, start_y + rect_height):
			for x in range(start_x, start_x + rect_width):
				self.put_pixel(x, y, color)
	
	def draw_borders(self):
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

	def render_frame(self, params):
		self.mlx.mlx_put_image_to_window(self.ptr, self.win, self.img, 0, 0)
		return 0

	def run(self):
		self.draw_borders()

		self.mlx.mlx_loop_hook(self.ptr, self.render_frame, None)
		self.mlx.mlx_loop(self.ptr)

def main():
	app = MazeApp(800, 600, "A-Maze-ing")
	app.run()

if __name__ == "__main__":
	main()