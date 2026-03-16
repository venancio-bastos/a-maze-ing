VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
WHEEL_MLX = mlx-2.2-py3-none-any.whl
CONFIG = config.txt

.PHONY: all install run debug clean fclean re lint

all: install

install: $(VENV)/touchfile

$(VENV)/touchfile: pyproject.toml $(WHEEL_MLX)
	@echo "Creating Virtual Environment..."
	python3 -m venv $(VENV)
	@echo "Updating pip..."
	$(PIP) install --upgrade pip
	@echo "Installing MiniLibX..."
	$(PIP) install $(WHEEL_MLX) --force-reinstall
	@echo "Installing base project..."
	$(PIP) install .
	@echo "Installing linters..."
	$(PIP) install flake8 mypy
	@touch $(VENV)/touchfile
	@echo "Ready"

run: install
	@echo "Starting A-Maze-ing..."
	$(PYTHON) a_maze_ing.py $(CONFIG)

debug: install
	@echo "Starting in Debug Mode..."
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

clean:
	@echo "Cleaning caches..."
	rm -rf src/__pycache__ mazegen/__pycache__ build dist src/*.egg-info .mypy_cache 
	find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
	@echo "Destroying Virtual Environment..."
	rm -rf $(VENV)

re: fclean all

lint: install
	@echo "Running Flake8..."
	$(VENV)/bin/flake8 --exclude=$(VENV),build,dist .
	@echo "Running MyPy..."
	$(VENV)/bin/mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --explicit-package-bases --exclude 'venv|build|dist' .