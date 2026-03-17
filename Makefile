VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
CONFIG = config.txt

.PHONY: all install run debug clean fclean re lint lint-strict package

all: install

install: $(VENV)/touchfile

$(VENV)/touchfile: pyproject.toml
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV)
	@echo "Updating pip..."
	$(PIP) install --upgrade pip
	@echo "Installing MLX wheel if present..."
	@MLX_WHEEL=$$(ls mlx-2.2-py3-ubuntu-any.whl mlx-2.2-py3-fedora-any.whl mlx-2.2-py3-none-any.whl 2>/dev/null | head -n 1); \
	if [ -n "$$MLX_WHEEL" ]; then \
		$(PIP) install "$$MLX_WHEEL" --force-reinstall; \
	else \
		echo "Warning: no MLX wheel found in repository root."; \
		echo "Add one of the expected mlx-2.2 wheel files before running the app."; \
	fi
	@echo "Installing project and tools..."
	$(PIP) install .
	$(PIP) install build flake8 mypy
	@touch $(VENV)/touchfile
	@echo "Ready."

run: install
	$(PYTHON) a_maze_ing.py $(CONFIG)

debug: install
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

clean:
	rm -rf build dist *.egg-info .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
	rm -rf $(VENV)
	rm -f mazegen.tar.gz

re: fclean all

lint: install
	$(VENV)/bin/flake8 --exclude=$(VENV),build,dist .
	$(VENV)/bin/mypy \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs \
		--explicit-package-bases \
		--exclude 'venv|build|dist' \
		.

lint-strict: install
	$(VENV)/bin/flake8 --exclude=$(VENV),build,dist .
	$(VENV)/bin/mypy --strict --exclude 'venv|build|dist' .

package: install
	if $(PYTHON) -m build; then \
		true; \
	else \
		$(PYTHON) setup.py sdist; \
	fi
	cp dist/*.tar.gz ./mazegen.tar.gz
	@echo "Created ./mazegen.tar.gz for the repository root."
