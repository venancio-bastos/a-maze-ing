VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
WHEEL = mlx-2.2-py3-none-any.whl
CONFIG = config.txt

.PHONY: all run clean fclean re setup

all: setup

setup: $(VENV)/touchfile

$(VENV)/touchfile: pyproject.toml $(WHEEL)
	@echo "Creating Virtual Environment..."
	python3 -m venv $(VENV)
	@echo "Updating pip..."
	$(PIP) install --upgrade pip
	@echo "Installing base project (.toml)..."
	$(PIP) install .
	@echo "Installing MiniLibX..."
	$(PIP) install $(WHEEL) --force-reinstall
	@touch $(VENV)/touchfile
	@echo "Ready"

run: setup
	@echo "Starting A-Maze-ing..."
	$(PYTHON) -m src.a_maze_ing $(CONFIG)

clean:
	@echo "Cleaning..."
	rm -rf src/__pycache__
	rm -rf mazegen/__pycache__
	rm -rf build dist *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
	@echo "Destroying Virtual Environment..."
	rm -rf $(VENV)

re: fclean all