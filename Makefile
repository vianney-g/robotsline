VENV = ./venv
PIP = $(VENV)/bin/pip
PYTHON = $(VENV)/bin/python

.PHONY: help tests install run_ia run_interactive

all: help

$(VENV)/touchfile_tests: $(VENV)/touchfile
	@$(PIP) install -r requirements_tests.txt
	@touch $(VENV)/touchfile_tests

$(VENV)/touchfile:
	@python3.10 -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@touch $(VENV)/touchfile
	@echo
	@echo "VirtualENV Setup Complete. Now run: source $(VENV)/bin/activate"
	@echo

help:
	@echo "------------------------------------------------------------------------"
	@echo "#  help             Display this help message"
	@echo "#  install          Install virtualenv"
	@echo "#  tests            Launch all tests"
	@echo "#  run_interactive  Run interactive game"
	@echo "#  run_ia           Run IA game"
	@echo "------------------------------------------------------------------------"

install: $(VENV)/touchfile

tests: $(VENV)/touchfile_tests
	@$(PYTHON) -m pytest

run_interactive:
	@$(PYTHON) cli.py -i

run_ia:
	@$(PYTHON) cli.py

