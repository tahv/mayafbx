.DEFAULT_GOAL = help

VENV = .venv
SOURCES = src tests

DOCS_BUILDDIR = docs/_build
MAYA_VERSION ?= 2025

PIP_CMD = uv pip
VENV_CMD = uv venv
# PIP_CMD = $(PYTHON) -m pip
# VENV_CMD = python -m venv

ifeq ($(OS), Windows_NT)
python = $(VENV)\Scripts\python.exe
else
python = $(VENV)/bin/python
endif

.PHONY: uninstall  ## Remove development environment
ifeq ($(OS), Windows_NT)
uninstall:
	if exist $(VENV) rd /q /s $(VENV)
	for /d /r %%g in (src\*.egg-info) do rd /q /s "%%g" 2>nul || break
else
uninstall:
	rm -rf $(VENV)
	rm -rf src/*.egg-info
endif

ifeq ($(OS), Windows_NT)
$(VENV): pyproject.toml
	@$(MAKE) --no-print-directory uninstall
	$(VENV_CMD) $(VENV)
	$(PIP_CMD) install --editable .[dev]
else
$(VENV): pyproject.toml
	@$(MAKE) --no-print-directory uninstall
	$(VENV_CMD) $(VENV)
	$(PIP_CMD) install --editable .[dev]
	touch $(VENV)
endif

.PHONY: install  ## Install the package and dependencies for local development
install:
	@$(MAKE) --no-print-directory --always-make $(VENV)

.PHONY: clean  ## Clear local caches and build artifacts
ifeq ($(OS), Windows_NT)
clean:
	del /f /q /s *.pyc >nul 2>nul
	del /f /q .coverage >nul 2>nul
	del /f /q .coverage.* >nul 2>nul
	del /f /q result.xml >nul 2>nul
	del /f /q coverage.xml >nul 2>nul
	rd /q /s dist 2>nul || break
	rd /q /s .ruff_cache 2>nul || break
	for /d /r %%g in (__pycache__) do rd /q /s "%%g" 2>nul || break
else
clean:
	rm -rf `find . -type f -name '*.pyc'`
	rm -f .coverage
	rm -f .coverage.*
	rm -f result.xml
	rm -f coverage.xml
	rm -rf dist
	rm -rf .ruff_cache
	rm -rf `find . -name __pycache__`
	rm -rf $(DOCS_BUILDDIR)
endif

.PHONY: tests  ## Run the tests with coverage in a docker container
tests: $(VENV)
	-docker stop mayafbx-test && docker rm mayafbx-test
	docker build --build-arg MAYA_VERSION=$(MAYA_VERSION) -t mayafbx .
	docker run --name mayafbx-test mayafbx mayapy -m coverage run -m pytest ; echo CODE: \$?
	docker cp mayafbx-test:/app/.coverage .coverage
	$(python) -m coverage report --show-missing --skip-covered --skip-empty

.PHONY: interactive  ## Run an interactive docker container
interactive:
	docker build --build-arg MAYA_VERSION=$(MAYA_VERSION) -t mayafbx .
	docker run --rm -it mayafbx

.PHONY: lint  ## Run linter
lint: $(VENV)
	$(python) -m ruff check $(SOURCES)

.PHONY: formatdiff  ## Show what the formatting would look like
formatdiff: $(VENV)
	$(python) -m ruff format --diff $(SOURCES)

.PHONY: mypy  ## Perform type-checking
mypy: $(VENV)
	$(python) -m mypy $(SOURCES)

.PHONY: build  ## Build package
build: $(VENV)
	$(python) -m hatch build -t wheel -t sdist -t zipped-directory

.PHONY: docs  ## Build documentation
docs: $(VENV)
	$(python) -m sphinx -W -n -b html -a docs $(DOCS_BUILDDIR)

.PHONY: serve  ## Serve documentation at http://127.0.0.1:8000
serve: $(VENV)
	$(python) -m sphinx_autobuild -b html -a --watch README.md --watch src -vvv docs $(DOCS_BUILDDIR)

.PHONY: linkcheck  ## Check all external links in docs for integrity
linkcheck: $(VENV)
	$(python) -m sphinx -b linkcheck -a docs $(DOCS_BUILDDIR)/linkcheck

.PHONY: zip  ## Create a zip archive with source code
zip: src/mayafbx/
	tar -cvf mayafbx.zip --format=zip --exclude *.pyc -C src mayafbx

.PHONY: help  ## Display this message
ifeq ($(OS), Windows_NT)
help:
	@setlocal EnableDelayedExpansion \
	&& for /f "tokens=2,* delims= " %%g in ('findstr /R /C:"^\.PHONY: .* ##.*$$" Makefile') do \
	set name=%%g && set "name=!name!              " && set "name=!name:~0,14!" \
	&& set desc=%%h && set "desc=!desc:~3!" \
	&& echo !name!!desc!
else
help:
	@grep  -E '^.PHONY: .*?## .*$$'  Makefile \
	| awk 'BEGIN {FS = ".PHONY: |## "}; {printf "%-14s %s\n", $$2, $$3}' \
	| sort
endif
