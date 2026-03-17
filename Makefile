PYTHON ?= python3.13
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff
MYPY := $(VENV)/bin/mypy
INSTALL_STAMP := $(VENV)/.deps-installed

.PHONY: venv install test lint typecheck check run

$(VENV_PYTHON):
	$(PYTHON) -m venv $(VENV)

venv: $(VENV_PYTHON)

$(INSTALL_STAMP): $(VENV_PYTHON) pyproject.toml
	$(VENV_PIP) install -e '.[dev]'
	touch $(INSTALL_STAMP)

install: $(INSTALL_STAMP)

test: install
	$(PYTEST) -q

lint: install
	$(RUFF) check .

typecheck: install
	$(MYPY) src

check: test lint typecheck

run: install
	$(VENV_PYTHON) -m sqlite_browser
