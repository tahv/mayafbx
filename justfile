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

# Serve documentation on http://127.0.0.1:8000
serve:
  uv run -m zensical serve

# Build documentation
docs:
  uv run zensical build --clean

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
[arg("maya", long="maya")]
interactive maya="2025":
    @just docker-build {{ maya }}
    docker run -it --rm "mayafbx:dev-{{ maya }}"

# Run test suite
[arg("maya", long="maya")]
test maya="2025" *args:
    @just docker-build {{ maya }}
    docker run --rm "mayafbx:dev-{{ maya }}" mayapy -m pytest {{ args }}

# Run test suite and report coverage
[arg("maya", long="maya")]
coverage maya="2025" *args:
    @just docker-build {{ maya }}
    docker run --rm "mayafbx:dev-{{ maya }}" sh -c " \
        mayapy -m coverage run --parallel -m pytest {{ args }} \
        && mayapy -m coverage combine \
        && mayapy -m coverage report"

[private]
docker-build maya="2025":
    docker build \
        --platform linux/amd64 \
        --tag "mayafbx:dev-{{ maya }}" \
        --build-arg MAYA_VERSION={{ maya }} \
        .
