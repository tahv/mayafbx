# mayafbx

[![Latest Release](https://img.shields.io/github/v/release/tahv/mayafbx)](https://github.com/tahv/mayafbx/releases/)
[![Github](https://img.shields.io/github/license/tahv/mayafbx?color=blue)](https://choosealicense.com/licenses/mit/)
![Tests](https://img.shields.io/github/workflow/status/tahv/mayafbx/Tests%20Runner?label=tests)
[![Docs](https://img.shields.io/github/workflow/status/tahv/mayafbx/Github%20Pages?label=docs)](https://tahv.github.io/mayafbx/)

Python wrapper for the FBX plugin of Maya.

FBX options as objects for importing and exporting FBX files.

Visit the [github repo](https://github.com/tahv/mayafbx/) for sources
and [command reference](https://tahv.github.io/mayafbx/) for more documentation.

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

The main purpose of this package is to have clear documentation, and I didn't
had the opportunity to try them all on different softwares. Don't hesitate
to improve the docstring of the properties if you have a better example.

The ``FbxExportOptions`` and ``FbxImportOptions`` are not feature complete yet,
mainly because I couldn't find good documentation for some of the command, so I
did not include them.
