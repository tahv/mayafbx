# mayafbx

[![Latest Release](https://img.shields.io/github/v/release/tahv/mayafbx)](https://github.com/tahv/mayafbx/releases/)
[![Github](https://img.shields.io/github/license/tahv/mayafbx?color=blue)](https://choosealicense.com/licenses/mit/)
![Tests](https://img.shields.io/github/workflow/status/tahv/mayafbx/Tests%20Runner?label=tests)
[![Docs](https://img.shields.io/github/workflow/status/tahv/mayafbx/Github%20Pages?label=docs)](https://tahv.github.io/mayafbx/)

Python wrapper for the FBX plugin of Maya.

Visit the [github repo](https://github.com/tahv/mayafbx/) for source code
and the [command reference](https://tahv.github.io/mayafbx/) for documentation.

Before:

```python
from maya import mel

mel.eval("FBXResetExport")  # Reset options.
mel.eval("FBXProperty Export|IncludeGrp|Animation -v true")
mel.eval("FBXProperty Export|IncludeGrp|Animation|ExtraGrp|RemoveSingleKey -v true")
mel.eval("FBXProperty Export|IncludeGrp|CameraGrp|Camera -v false")

mel.eval('FBXExport -f "C:/outfile.fbx" -s')  # '-s' for selected.
```

After:

```python
from mayafbx import FbxExportOptions, export_fbx

options = FbxExportOptions()
options.animation = True
options.remove_single_key = True
options.cameras = True
options.selected = True

export_fbx("C:/outfile.fbx", options)
```

Alternative:

```python
from mayafbx import FbxExportOptions, export_fbx

options = FbxExportOptions(
    animation=True,
    remove_single_key=True,
    cameras=True,
    selected=True)

export_fbx("C:/outfile.fbx", options)
```

## Installation

- Download the [latest release](https://github.com/tahv/mayafbx/releases/latest/download/mayafbx.zip).

- Or use pip:

```bash
pip install git+git://github.com/tahv/mayafbx#egg=mayafbx
```

## Requirements

Run Maya >= 2020. It may run on older version but was not tested on them.

## Usage

```python
import tempfile, os
from maya import cmds
from mayafbx import FbxExportOptions, export_fbx
from mayafbx import FbxImportOptions, import_fbx, MergeMode

cmds.file(new=True, force=True)

# Create a cube with 2 keyframes.
cube = cmds.polyCube()[0]
cmds.setKeyframe(cube, attribute="translateX", time=1, value=0)
cmds.setKeyframe(cube, attribute="translateX", time=24, value=10)

# Setup options to export the scene with baked animation.
options = FbxExportOptions()
options.animation = True
options.bake_animation = True
options.bake_resample_all = True

# Export the scene as FBX.
filepath = os.path.join(tempfile.gettempdir(), "testcube.fbx")
export_fbx(filepath, options)

# Remove all keys from our cube.
cmds.cutKey(cube, attribute="translateX", option="keys")

# Setup options to import our animation back on our cube.
options = FbxImportOptions()
options.merge_mode = MergeMode.kMerge
options.animation = True

# Import our FBX.
import_fbx(filepath, options)
```

## Contributing

Pull requests are welcome. Please make sure to update tests as appropriate.

The main purpose of this package is to have clear documentation, and I did not
had the opportunity to try all export on different softwares, so don't hesitate
to improve the docstrings if you have a better example.

The ``FbxExportOptions`` and ``FbxImportOptions`` are not feature complete yet,
mainly because I couldn't find good documentation for some of the commands.
