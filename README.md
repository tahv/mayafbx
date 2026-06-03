<div align="center">
  <h1>mayafbx</h1>
  <a href="https://pypi.org/project/mayafbx">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/mayafbx?style=for-the-badge">
  </a>
  <a href="https://www.buymeacoffee.com/tgambier">
    <img alt="Buy Me a Coffee" style="height: 28px;" height="28" src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png">
  </a>
  <p><b>A Python wrapper for the Maya FBX plugin</b></p>
  <a href="https://mayafbx.readthedocs.io">Documentation</a>
  • <a href="https://mayafbx.readthedocs.io/api">API Reference</a>
  • <a href="https://pypi.org/project/mayafbx">PyPI</a>
  • <a href="https://gitlab.com/tahv/mayafbx">GitLab</a>
  • <a href="https://github.com/tahv/mayafbx">GitHub</a>
  • <a href="https://gitlab.com/tahv/mayafbx/-/blob/main/CONTRIBUTING.md">Contributing</a>
  • <a href="https://gitlab.com/tahv/mayafbx/-/blob/main/CHANGELOG.md">Changelog</a>
</div>

---

## Installation

```console
pip install mayafbx
```

<!--
mayafbx is also available as an archive (`mayafbx-{version}.zip`)
that can be downloaded from the
[latest release](https://gitlab.com/tahv/mayafbx/-/releases).
The zip archive have is structured as follows:

```text
.
├── LICENSE
├── METADATA.json
├── README.md
└── mayafbx/
    ├── __init__.py
    └── ...
```
-->

## Comparison

Below is an example of exporting an FBX file using standard Maya commands:

```python
from maya import mel

mel.eval("FBXResetExport")
mel.eval("FBXProperty Export|IncludeGrp|Animation -v true")
mel.eval("FBXProperty Export|IncludeGrp|Animation|ExtraGrp|RemoveSingleKey -v true")
mel.eval("FBXProperty Export|IncludeGrp|CameraGrp|Camera -v false")

mel.eval('FBXExport -f "C:/outfile.fbx" -s')
```

Here's how to achieve the same result with `mayafbx`:

```python
import mayafbx

options = mayafbx.FbxExportOptions()
options.animation = True
options.remove_single_key = True
options.cameras = True

mayafbx.export_fbx("C:/outfile.fbx", options, selection=True)
```

Alternatively, all fields can be passed directly to the constructor as `kwargs`:

```python
import mayafbx

options = mayafbx.FbxExportOptions(animation=True, remove_single_key=True, cameras=True)

mayafbx.export_fbx("C:/outfile.fbx", options, selection=True)
```

## Example

This example shows how to export animation from a cube and import it back.

```python
import os
import tempfile
from maya import cmds
import mayafbx

# start from an empty scene
cmds.file(new=True, force=True)

# create a cube with 2 keyframes
cube = cmds.polyCube()[0]
cmds.setKeyframe(cube, attribute="translateX", time=1, value=0)
cmds.setKeyframe(cube, attribute="translateX", time=24, value=10)

# prepare options to export baked animation
options = mayafbx.FbxExportOptions()
options.animation = True
options.bake_animation = True
options.bake_resample_all = True

# export the scene as FBX
filepath = os.path.join(tempfile.gettempdir(), "testcube.fbx")
mayafbx.export_fbx(filepath, options)

# remove all keys from the cube
cmds.cutKey(cube, attribute="translateX", option="keys")

# prepare options to import animation back to the cube
options = mayafbx.FbxImportOptions()
options.merge_mode = mayafbx.MergeMode.kMerge
options.animation = True

# import the previously exported FBX
mayafbx.import_fbx(filepath, options)
```

## Contributing

Contributions of any kind are welcome.
Please [open an issue](https://gitlab.com/tahv/mayafbx/-/issues), or read the
[contribution guidelines](https://gitlab.com/tahv/mayafbx/-/blob/main/CONTRIBUTING.md)
and open a [merge request](https://gitlab.com/tahv/mayafbx/-/merge_requests).
