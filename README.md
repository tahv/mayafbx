# mayafbx

[![Source](https://img.shields.io/badge/source-%23fc6d25?logo=gitlab&logoColor=white)](https://gitlab.com/tahv/mayafbx)
[![Documentation](https://img.shields.io/badge/documentation-teal?logo=readthedocs&logoColor=white)](https://mayafbx.readthedocs.io/latest)
[![PyPI](https://img.shields.io/pypi/v/mayafbx?logo=python&logoColor=white&label=)](https://pypi.org/project/mayafbx)

A Python wrapper for the Maya FBX plugin.

## Project Information

- [**Documentation**](https://mayafbx.readthedocs.io/latest)
- [**PyPI**](https://pypi.org/project/mayafbx)
- [**Source Code**](https://gitlab.com/tahv/mayafbx)
- [**Changelog**](https://mayafbx.readthedocs.io/latest/contributing.html)
- [**Contributing**](https://mayafbx.readthedocs.io/latest/contributing.html)
- [**GitHub Mirror**](https://github.com/tahv/mayafbx)

## Installation

```console
pip install mayafbx
```

You can also download and extract `mayafbx-<version>.zip` from
[latest release](https://gitlab.com/tahv/mayafbx/-/releases).
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

Below is an example of exporting an FBX file using standard Maya commands:

```python
from maya import mel

mel.eval("FBXResetExport")  # Reset options.
mel.eval("FBXProperty Export|IncludeGrp|Animation -v true")
mel.eval("FBXProperty Export|IncludeGrp|Animation|ExtraGrp|RemoveSingleKey -v true")
mel.eval("FBXProperty Export|IncludeGrp|CameraGrp|Camera -v false")

mel.eval('FBXExport -f "C:/outfile.fbx" -s')  # '-s' for selected.
```

Here's how to achieve the same result with `mayafbx`:

```python
from mayafbx import FbxExportOptions, export_fbx

options = FbxExportOptions()
options.animation = True
options.remove_single_key = True
options.cameras = True

export_fbx("C:/outfile.fbx", options, selection=True)
```

Alternatively, all fields can be passed directly to the `__init__` function:

```python
from mayafbx import FbxExportOptions, export_fbx

options = FbxExportOptions(animation=True, remove_single_key=True, cameras=True)

export_fbx("C:/outfile.fbx", options, selection=True)
```

## Example

This example shows how to export animation from a cube and import it back.

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

# start from an empty scene
cmds.file(new=True, force=True)

# create a cube with 2 keyframes
cube = cmds.polyCube()[0]
cmds.setKeyframe(cube, attribute="translateX", time=1, value=0)
cmds.setKeyframe(cube, attribute="translateX", time=24, value=10)

# prepare options to export baked animation
options = FbxExportOptions()
options.animation = True
options.bake_animation = True
options.bake_resample_all = True

# export the scene as FBX
filepath = os.path.join(tempfile.gettempdir(), "testcube.fbx")
export_fbx(filepath, options)

# remove all keys from the cube
cmds.cutKey(cube, attribute="translateX", option="keys")

# Prepare options to import animation back to the cube
options = FbxImportOptions()
options.merge_mode = MergeMode.kMerge
options.animation = True

# import the previously exported FBX
import_fbx(filepath, options)
```

## Contributing

Contributions of any kind are welcome.
Please [open an issue](https://gitlab.com/tahv/mayafbx/-/issues), or read the
[contribution guidelines](https://mayafbx.readthedocs.io/latest/contributing.html)
and open a [merge request](https://gitlab.com/tahv/mayafbx/-/merge_requests).
