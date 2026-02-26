from maze_app import MazeApp

def main():
	app = MazeApp(800, 600, "A-Maze-ing", maze_cols=20, maze_rows=20)
	app.run()

if __name__ == "__main__":
	main()