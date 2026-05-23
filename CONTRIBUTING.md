# Contributing

## Project commands

The easiest way to run project commands is to
[install just](https://just.systems/man/en/installation.html).

For example, the `rust-just` Python package can be installed with
[`uv`](https://docs.astral.sh/uv/concepts/tools/):

```console
uv tool install rust-just
just
```

Or executed without installation with
[`uvx`](https://docs.astral.sh/uv/guides/tools/):

```console
uvx --from rust-just just
```

Running `just` without any arguments list available recipes in the
[justfile](./justfile) at the root of the repo.

```console
just
```

## Running the tests

To simplify the development, tests are run in a docker container
generated from the [Dockerfile](https://github.com/tahv/mayafbx/blob/main/Dockerfile)
at the root of this repo.

The `just test` recipe build the container and run the tests with coverage.

The Dockerfile uses [`tahv/mayapy`](https://hub.docker.com/r/tahv/mayapy) images
and default to `tahv/mayapy:2025`.
A different Maya version may be specified.

```bash
just test 2022
```
