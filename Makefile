VENV = ./venv
PIP = $(VENV)/bin/pip
PYTHON = $(VENV)/bin/python

.PHONY: tests

all: help

$(VENV)/touchfile_tests: $(VENV)/touchfile
	@$(PIP) install -r requirements_tests.txt
	@touch $(VENV)/touchfile_tests

$(VENV)/touchfile:
	@python3.10 -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@touch $(VENV)/touchfile
	@echo
	@echo "VirtualENV Setup Complete. Now run: source $(VENV)/bin/activate"
	@echo

help:
	@echo "------------------------------------------------------------------------"
	@echo "#  virtualenv	        : Create virtualenv"
	@echo "#  tests			: Launch all tests"
	@echo "#  help			: Display this help message"
	@echo "------------------------------------------------------------------------"

tests: $(VENV)/touchfile_tests
	@$(PYTHON) -m pytest
