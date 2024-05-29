[mayafbx-documentation]: https://mayafbx.readthedocs.io/latest
[mayafbx-license]: https://github.com/tahv/mayafbx/blob/main/LICENSE
[mayafbx-repo]: https://github.com/tahv/mayafbx
[mayafbx-pypi]: https://pypi.org/project/mayafbx
[ruff-repo]: https://github.com/astral-sh/ruff
[mypy-repo]: https://github.com/python/mypy
[mayafbx-workflow-tests]: https://github.com/tahv/mayafbx/actions/workflows/tests.yml
<!-- [mayafbx-zip]: https://github.com/tahv/mayafbx/releases/latest/download/mayafbx.zip -->
[mayafbx-latest-release]: https://github.com/tahv/mayafbx/releases/latest
[mayafbx-contributing]: https://mayafbx.readthedocs.io/latest/contributing.html

# mayafbx

> **Warning:**
>
> Release `1.0.0` include many API breaking changes and dropped Python 2 support.
> If you are looking for the legacy version of `mayafbx`, see this 
> [commit](https://github.com/tahv/mayafbx/tree/95d52a61bdefd84c90b9822b2ccb829da89626a8)
> and release [`0.1.0`](https://github.com/tahv/mayafbx/releases/tag/0.1.0).

[![License - MIT](https://img.shields.io/github/license/tahv/mayafbx?label=License)][mayafbx-license]
[![Maya Version](https://img.shields.io/badge/Maya-2022%20%7C%202023%20%7C%202024%20%7C%202025-%2339a5cc?logo=autodesk&logoColor=white)][mayafbx-pypi]
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mayafbx?logo=python&label=Python&logoColor=white)][mayafbx-pypi]
[![PyPI - Version](https://img.shields.io/pypi/v/mayafbx?logo=pypi&label=PyPI&logoColor=white)][mayafbx-pypi]
[![Linter - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)][ruff-repo]
[![Types - Mypy](https://img.shields.io/badge/Types-Mypy-blue.svg)][mypy-repo]
[![CI - Tests](https://img.shields.io/github/actions/workflow/status/tahv/mayafbx/tests.yml?logo=github&logoColor=white&label=Tests)][mayafbx-workflow-tests]
[![Documentation Status](https://img.shields.io/readthedocs/mayafbx?logo=readthedocs&logoColor=white&label=Documentation)][mayafbx-documentation]

Python wrapper of Maya FBX plugin.

## Installation

Install `mayafbx` with pip.

```bash
python -m pip install mayafbx
```

You can also download and extract `mayafbx-<version>.zip` from [latest release][mayafbx-latest-release].

The zip archive is created using 
[`hatch-zipped-directory`](https://github.com/dairiki/hatch-zipped-directory) 
and has the following structure:

```text
.
├── LICENSE
├── METADATA.json
├── README.md
└── mayafbx/
    ├── __init__.py
    └── ...
```

## Comparison

Below is an example of how to export an FBX file using standard Maya commands:

```python
from maya import mel

mel.eval("FBXResetExport")  # Reset options.
mel.eval("FBXProperty Export|IncludeGrp|Animation -v true")
mel.eval("FBXProperty Export|IncludeGrp|Animation|ExtraGrp|RemoveSingleKey -v true")
mel.eval("FBXProperty Export|IncludeGrp|CameraGrp|Camera -v false")

mel.eval('FBXExport -f "C:/outfile.fbx" -s')  # '-s' for selected.
```

And here is how to achieve the same using `mayafbx`:

```python
from mayafbx import FbxExportOptions, export_fbx

options = FbxExportOptions()
options.animation = True
options.remove_single_key = True
options.cameras = True

export_fbx("C:/outfile.fbx", options, selection=True)
```

Alternatively, you can write it in a more concise way:

```python
from mayafbx import FbxExportOptions, export_fbx

options = FbxExportOptions(animation=True, remove_single_key=True, cameras=True)

export_fbx("C:/outfile.fbx", options, selection=True)
```

## Quickstart

In this example, we export the animation from a cube and import it back.

```python
import os
import tempfile
from maya import cmds
from mayafbx import (
    FbxExportOptions, 
    FbxImportOptions, 
    MergeMode,
    export_fbx,
    import_fbx, 
)

# Start from an empty scene.
cmds.file(new=True, force=True)

# Create a cube with 2 keyframes.
cube = cmds.polyCube()[0]
cmds.setKeyframe(cube, attribute="translateX", time=1, value=0)
cmds.setKeyframe(cube, attribute="translateX", time=24, value=10)

# Prepare options to export baked animation.
options = FbxExportOptions()
options.animation = True
options.bake_animation = True
options.bake_resample_all = True

# Export the scene as FBX.
filepath = os.path.join(tempfile.gettempdir(), "testcube.fbx")
export_fbx(filepath, options)

# Remove all keys from the cube.
cmds.cutKey(cube, attribute="translateX", option="keys")

# Prepare options to import animation back to the cube.
options = FbxImportOptions()
options.merge_mode = MergeMode.kMerge
options.animation = True

# Import the previously exported FBX.
import_fbx(filepath, options)
```

## Documentation

See mayafbx [documentation]([mayafbx-documentation]) for more details.

## Contributing

For guidance on setting up a development environment and contributing to the project,
see the [contributing]([mayafbx-contributing]) section.

