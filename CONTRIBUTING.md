# Contributing

## Makefile commands

This project include a [Makefile](https://www.gnu.org/software/make/)
containing the most common commands used when developing.

```text
$ make help
build          Build project
clean          Clear local caches and build artifacts
doc            Build documentation
formatdiff     Show what the formatting would look like
help           Display this message
install        Install the package and dependencies for local development
interactive    Run an interactive docker container
linkcheck      Check all external links in docs for integrity
lint           Run linter
mypy           Perform type-checking
serve          Serve documentation at http://127.0.0.1:8000
tests          Run the tests with coverage in a docker container
uninstall      Remove development environment
```

## Running the tests

To simplify the development, tests are runned in a docker container
generated from the [Dockerfile](https://github.com/tahv/mayafbx/blob/main/Dockerfile)
at the root of this repo.

The `make tests` target build the container and run the tests with coverage.

The Dockerfile uses [`tahv/mayapy`](https://hub.docker.com/r/tahv/mayapy) images and
default to `tahv/mayapy:2025`. You can change the tag by setting `MAYA_VERSION`

```bash
make tests MAYA_VERSION=2022
```
