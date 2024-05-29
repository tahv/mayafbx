"""Test suite for the mayafbx package."""

from __future__ import annotations

from typing import TYPE_CHECKING

import mayafbx
import pytest
from maya import cmds, mel
from maya.api import OpenMaya
from mayafbx.exceptions import MelEvalError
from mayafbx.exporter import get_export_takes, set_export_takes
from mayafbx.utils import (
    Take,
    collect_fbx_properties,
    get_anim_control_end_time,
    run_mel_command,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_fbxproperty_default() -> None:
    """It returns default value."""
    command = "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups"

    fbx_prop = mayafbx.FbxProperty(command, type_=bool, default=True)
    assert fbx_prop.default is True

    fbx_prop = mayafbx.FbxProperty(command, type_=bool, default=lambda: True)
    assert fbx_prop.default is True


def test_fbxproperty_command() -> None:
    """It returns command."""
    command = "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups"
    fbx_prop = mayafbx.FbxProperty(command, type_=bool, default=True)
    assert fbx_prop.command == command


def test_fbxproperty_get() -> None:
    """It get value from scene."""
    command = "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups"
    fbx_prop = mayafbx.FbxProperty(command, type_=bool, default=True)

    mel.eval(f"{command} -v true")
    assert fbx_prop.get() is True

    mel.eval(f"{command} -v false")
    assert fbx_prop.get() is False


def test_fbxproperty_set() -> None:
    """It set value to scene."""
    command = "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups"
    fbx_prop = mayafbx.FbxProperty(command, type_=bool, default=True)

    fbx_prop.set(value=True)
    assert mel.eval(f"{command} -q") == 1

    fbx_prop.set(value=False)
    assert mel.eval(f"{command} -q") == 0


def test_fbxoptions_from_scene() -> None:
    """It initialize FbxOptions instance from scene value."""
    command = "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups"

    class TestOptions(mayafbx.FbxOptions):
        smoothing_groups = mayafbx.FbxPropertyField(command, type=bool, default=False)

    mel.eval(f"{command} -v true")
    assert TestOptions.from_scene().smoothing_groups is True

    mel.eval(f"{command} -v false")
    assert TestOptions.from_scene().smoothing_groups is False


def test_fbxoptions_init_kwargs() -> None:
    """It accept fields as init kwargs."""
    command = "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups"

    class TestOptions(mayafbx.FbxOptions):
        smoothing_groups = mayafbx.FbxPropertyField(command, type=bool, default=False)

    assert TestOptions(smoothing_groups=True).smoothing_groups is True
    assert TestOptions(smoothing_groups=False).smoothing_groups is False


def test_fbxoptions_iter() -> None:
    """It iter FbxProperties in FbxOptions instance."""

    class TestOptions(mayafbx.FbxOptions):
        smoothing_groups = mayafbx.FbxPropertyField(
            "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups",
            type=bool,
            default=False,
        )
        hard_edges = mayafbx.FbxPropertyField(
            command="FBXProperty Export|IncludeGrp|Geometry|expHardEdges",
            type=bool,
            default=False,
        )

    properties = list(TestOptions())
    assert len(properties) == 2
    # TODO: test are expected properties


def test_apply_options() -> None:
    """It apply FBXProperties in option instance."""
    command = "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups"

    class TestOptions(mayafbx.FbxOptions):
        smoothing_groups = mayafbx.FbxPropertyField(command, type=bool, default=False)

    options = TestOptions()

    options.smoothing_groups = True
    mayafbx.apply_options(options)
    assert mel.eval(f"{command} -q") == 1

    options.smoothing_groups = False
    mayafbx.apply_options(options)
    assert mel.eval(f"{command} -q") == 0


def test_applied_options() -> None:
    """It apply FBXProperties in option instance during context."""
    command = "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups"

    class TestOptions(mayafbx.FbxOptions):
        smoothing_groups = mayafbx.FbxPropertyField(command, type=bool, default=False)

    mel.eval(f"{command} -v false")
    assert mel.eval(f"{command} -q") == 0

    options = TestOptions()
    options.smoothing_groups = True
    with mayafbx.applied_options(options):
        assert mel.eval(f"{command} -q") == 1

    assert mel.eval(f"{command} -q") == 0


def test_fbxexportoptions_valid_defaults() -> None:
    """It has valid default values."""
    exceptions = {
        # End frame is reset to 48 when calling 'FBXResetExport'.
        "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameEnd": get_anim_control_end_time(),  # noqa: E501
    }

    options = mayafbx.FbxExportOptions()
    for prop, _ in options:
        value = exceptions.get(prop.command, prop.get())
        assert value == prop.default


def test_fbximportoptions_valid_defaults() -> None:
    """It has valid default values."""
    options = mayafbx.FbxImportOptions()
    for prop, _ in options:
        assert prop.get() == prop.default


def test_fbxexportoptions_can_be_applied() -> None:
    """It can apply default `FbxExportOptions`."""
    options = mayafbx.FbxExportOptions()
    mayafbx.apply_options(options)


def test_fbximportoptions_can_be_applied() -> None:
    """It can apply default `FbxImprotOptions`."""
    options = mayafbx.FbxImportOptions()
    mayafbx.apply_options(options)


def test_run_mel_command_raise_exception() -> None:
    """It raises `MelEvalError` when a mel command is invalid."""
    with pytest.raises(MelEvalError):
        run_mel_command("invalid")


def test_collect_fbx_properties_returns_list_of_fbx_properties() -> None:
    """It returns a list of FBXProperty dict."""
    data = collect_fbx_properties()
    assert isinstance(data, list)
    assert isinstance(data[0], dict)
    assert "path" in data[0]


def test_export_selected_model(tmp_path: Path) -> None:
    """I export only selected model."""
    cube_1 = cmds.polyCube()[0]
    cube_2 = cmds.polyCube()[0]

    cmds.select(cube_1)
    filepath = tmp_path / "selected_model.fbx"
    mayafbx.export_fbx(filepath, mayafbx.FbxExportOptions(), selection=True)

    cmds.delete(cube_1, cube_2)
    assert cmds.objExists(cube_1) is False
    assert cmds.objExists(cube_2) is False

    mayafbx.import_fbx(filepath, mayafbx.FbxImportOptions())

    assert cmds.objExists(cube_1) is True
    assert cmds.objExists(cube_2) is False


def test_export_with_selection_raise_nothing_selected(tmp_path: Path) -> None:
    """It raises an error if nothing is selected."""
    filepath = tmp_path / "foo.fbx"
    with pytest.raises(RuntimeError):
        mayafbx.export_fbx(filepath, mayafbx.FbxExportOptions(), selection=True)


def test_export_import_animated_cube(tmp_path: Path) -> None:
    """I can export and import an animated mesh."""
    cube = cmds.polyCube()[0]
    cmds.setKeyframe(f"{cube}.translateX", time=1, value=0)
    cmds.setKeyframe(f"{cube}.translateX", time=24, value=10)
    assert cmds.keyframe(f"{cube}.translateX", query=True, keyframeCount=True) == 2

    export_options = mayafbx.FbxExportOptions()
    export_options.animation = True

    filepath = tmp_path / "animated_cube.fbx"
    mayafbx.export_fbx(filepath, export_options)

    cmds.cutKey(f"{cube}.translateX", option="keys")
    assert cmds.keyframe(f"{cube}.translateX", query=True, keyframeCount=True) == 0

    import_options = mayafbx.FbxImportOptions()
    import_options.merge_mode = mayafbx.MergeMode.MERGE
    import_options.animation = True

    mayafbx.import_fbx(filepath, import_options)
    assert cmds.keyframe(f"{cube}.translateX", query=True, keyframeCount=True) == 2

    key_values = cmds.keyframe(
        f"{cube}.translateX",
        query=True,
        valueChange=True,
        timeChange=True,
    )
    assert key_values == [1.0, 0.0, 24.0, 10.0]


def test_restore_export_preset() -> None:
    """It reset scene export preset."""
    command = "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups"

    assert mel.eval(f"{command} -q") == 0

    mel.eval(f"{command} -v true")
    assert mel.eval(f"{command} -q") == 1

    mayafbx.restore_export_preset()
    assert mel.eval(f"{command} -q") == 0


def test_restore_import_preset() -> None:
    """It reset scene import preset."""
    command = "FBXProperty Import|IncludeGrp|Geometry|UnlockNormals"

    assert mel.eval(f"{command} -q") == 0

    mel.eval(f"{command} -v true")
    assert mel.eval(f"{command} -q") == 1

    mayafbx.restore_import_preset()
    assert mel.eval(f"{command} -q") == 0


def test_get_set_export_takes() -> None:
    """It set and get export takes."""
    takes = [
        Take("foo", 1, 9),
        Take("bar", 10, 20),
    ]
    set_export_takes(takes)

    assert get_export_takes() == takes


def test_set_export_takes_raise_end_lower_than_start() -> None:
    """It raises an error when end frame is lower than start frame."""
    take = Take("foo", 5, 1)
    with pytest.raises(RuntimeError):
        set_export_takes([take])


def test_export_import_take(tmp_path: Path) -> None:
    """I can export and import takes."""
    cube = cmds.polyCube()[0]
    cmds.setKeyframe(f"{cube}.translateX", time=0, value=1)
    cmds.setKeyframe(f"{cube}.translateX", time=10, value=2)
    cmds.setKeyframe(f"{cube}.translateX", time=20, value=3)
    assert cmds.keyframe(f"{cube}.translateX", query=True, keyframeCount=True) == 3

    export_options = mayafbx.FbxExportOptions()
    export_options.animation = True
    export_options.delete_original_take_on_split_animation = True

    filepath = tmp_path / "takes.fbx"
    mayafbx.export_fbx(
        filepath,
        export_options,
        takes=[Take("foo", 0, 10), Take("bar", 10, 20)],
    )

    import_options = mayafbx.FbxImportOptions()
    import_options.merge_mode = mayafbx.MergeMode.MERGE
    import_options.animation = True

    # take 'foo'

    cmds.cutKey(f"{cube}.translateX", option="keys")
    assert cmds.keyframe(f"{cube}.translateX", query=True, keyframeCount=True) == 0

    mayafbx.import_fbx(filepath, import_options, take=1)
    assert cmds.keyframe(f"{cube}.translateX", query=True, keyframeCount=True) == 2

    key_values = cmds.keyframe(
        f"{cube}.translateX",
        query=True,
        valueChange=True,
        timeChange=True,
    )
    assert key_values == [0.0, 1.0, 10.0, 2.0]

    # take 'bar'

    cmds.cutKey(f"{cube}.translateX", option="keys")
    assert cmds.keyframe(f"{cube}.translateX", query=True, keyframeCount=True) == 0

    mayafbx.import_fbx(filepath, import_options, take=2)
    assert cmds.keyframe(f"{cube}.translateX", query=True, keyframeCount=True) == 2

    key_values = cmds.keyframe(
        f"{cube}.translateX",
        query=True,
        valueChange=True,
        timeChange=True,
    )
    assert key_values == [10.0, 2.0, 20.0, 3.0]


def test_up_axis_from_scene() -> None:
    """It returns scene up axis."""
    OpenMaya.MGlobal.setYAxisUp()
    assert mayafbx.UpAxis.from_scene() == mayafbx.UpAxis.Y

    OpenMaya.MGlobal.setZAxisUp()
    assert mayafbx.UpAxis.from_scene() == mayafbx.UpAxis.Z
