.DEFAULT_GOAL = help

venv = .venv
sources = src tests

DOCS_BUILDDIR = docs/_build

ifeq ($(OS), Windows_NT)
python = $(venv)\Scripts\python.exe
else
python = $(venv)/bin/python
endif

.PHONY: uninstall  ## Remove development environment
ifeq ($(OS), Windows_NT)
uninstall:
	if exist $(venv) rd /q /s $(venv)
	for /d /r %%g in (src\*.egg-info) do rd /q /s "%%g" 2>nul || break
else
uninstall:
	rm -rf $(venv)
	rm -rf src/*.egg-info
endif

ifeq ($(OS), Windows_NT)
$(venv): pyproject.toml
	@$(MAKE) --no-print-directory uninstall
	python -m venv $(venv)
	$(python) -m pip install --upgrade pip build --editable .[dev]
else
$(venv): pyproject.toml
	@$(MAKE) --no-print-directory uninstall
	python -m venv $(venv)
	$(python) -m pip install --upgrade pip build --editable .[dev]
	touch $(venv)
endif

.PHONY: install  ## Install the package and dependencies for local development
install:
	@$(MAKE) --no-print-directory --always-make $(venv)

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

.PHONY: tests  ## Run tests and coverage
tests: $(venv)
	-docker stop mayafbx-test && docker rm mayafbx-test
	docker build --quiet -t mayafbx .
	docker run --name mayafbx-test mayafbx mayapy -m coverage run -m pytest
	docker cp mayafbx-test:/app/.coverage .coverage
	$(python) -m coverage report --show-missing --skip-covered --skip-empty

.PHONY: interactive  ## Run an interactive docker container
interactive:
	docker build -t mayafbx .
	docker run --rm -it mayafbx

.PHONY: lint  ## Run linter
lint: $(venv)
	$(python) -m ruff check $(sources)

.PHONY: formatdiff  ## Show what the formatting would look like
formatdiff: $(venv)
	$(python) -m ruff format --diff $(sources)

.PHONY: mypy  ## Perform type-checking
mypy: $(venv)
	$(python) -m mypy $(sources)

.PHONY: build  ## Build package
build: $(venv)
	$(python) -m build

.PHONY: docs  ## Build documentation
docs: $(venv)
	$(python) -m sphinx -W -n -b html -a docs $(DOCS_BUILDDIR)

.PHONY: serve  ## Serve documentation at http://127.0.0.1:8000
serve: $(venv)
	$(python) -m sphinx_autobuild -b html -a --watch README.md --watch src -vvv docs $(DOCS_BUILDDIR)

# .PHONY: linkcheck  ## Check all external links in docs for integrity
# linkcheck: $(venv)
# 	$(python) -m sphinx -b linkcheck -a docs $(DOCS_BUILDDIR)/linkcheck

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
