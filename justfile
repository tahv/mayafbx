set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# List available recipes
[default]
list:
    @just --list

# Sync development environment
sync:
    uv sync

# Open project in neovim
nvim *args:
    uv run -- nvim {{ args }}

# Build documentation
docs:
	uv run -m sphinx -W -n -b html -a docs site

# Serve documentation on http://127.0.0.1:8000
serve:
  uv run -m sphinx_autobuild -b html -a --watch README.md --watch src -vvv docs site

# Check all external links in docs for integrity
linkcheck:
  uv run -m sphinx -b linkcheck -a docs site/linkcheck

# Run `ruff` linter
ruff *files:
  uvx ruff@latest check --output-format concise {{files}}

# Dry run `ruff` formatter and output diff
fmt:
  uvx ruff@latest format --check

# Perform type-checking with `mypy`
mypy:
    uv run -m mypy

# Build package
build:
    uvx hatch@latest build -t wheel -t sdist -t zipped-directory
    uvx check-wheel-contents dist/*.whl

# Run an interactive docker container
interactive version="2025":
    docker build \
        --platform linux/amd64 \
        --tag "mayafbx:dev-{{ version }}" \
        --build-arg MAYA_VERSION={{ version }} \
        .
    docker run -it --rm "mayafbx:dev-{{ version }}"

test version="2025":
    docker build \
        --platform linux/amd64 \
        --tag "mayafbx:dev-{{ version }}" \
        --build-arg MAYA_VERSION={{ version }} \
        .
    docker run --rm "mayafbx:dev-{{ version }}" mayapy -m pytest -vv --color yes
