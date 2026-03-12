VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
CONFIG = config.txt
UNAME_S := $(shell uname -s)

.PHONY: all run clean fclean re setup

all: setup

setup: $(VENV)/touchfile

$(VENV)/touchfile: pyproject.toml
	@echo "Creating Virtual Environment..."
	python3 -m venv $(VENV)
	@echo "Updating pip..."
	$(PIP) install --upgrade pip setuptools wheel
	@echo "Installing base project..."
	$(PIP) install .

ifeq ($(UNAME_S),Darwin)
	@echo "macOS detected - skipping incompatible mlx wheel."
else
	@echo "Installing MiniLibX wheel..."
	$(PIP) install mlx-2.2-py3-none-any.whl --force-reinstall
endif

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
	rm -rf src/*.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
	@echo "Destroying Virtual Environment..."
	rm -rf $(VENV)

re: fclean all