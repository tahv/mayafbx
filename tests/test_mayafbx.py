"""Test suite for the mayafbx package."""
from __future__ import annotations

from typing import TYPE_CHECKING

import mayafbx
import pytest
from maya import cmds, mel
from mayafbx.exceptions import MelEvalError
from mayafbx.utils import (
    collect_fbx_properties,
    get_anim_control_end_time,
    run_mel_command,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_fbxproperty_default() -> None:
    """It returns default value."""
    command = "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups"

    fbx_prop = mayafbx.FbxProperty(command, type=bool, default=True)
    assert fbx_prop.default is True

    fbx_prop = mayafbx.FbxProperty(command, type=bool, default=lambda: True)
    assert fbx_prop.default is True


def test_fbxproperty_command() -> None:
    """It returns command."""
    command = "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups"
    fbx_prop = mayafbx.FbxProperty(command, type=bool, default=True)
    assert fbx_prop.command == command


def test_fbxproperty_get() -> None:
    """It get value from scene."""
    command = "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups"
    fbx_prop = mayafbx.FbxProperty(command, type=bool, default=True)

    mel.eval(f"{command} -v true")
    assert fbx_prop.get() is True

    mel.eval(f"{command} -v false")
    assert fbx_prop.get() is False


def test_fbxproperty_set() -> None:
    """It set value to scene."""
    command = "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups"
    fbx_prop = mayafbx.FbxProperty(command, type=bool, default=True)

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
        # NOTE: End frame is reset to 48 when calling 'FBXResetExport'.
        "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameEnd": get_anim_control_end_time(),
    }

    options = mayafbx.FbxExportOptions()
    for prop, _ in options:
        value = exceptions.get(prop.command, prop.get())
        assert value == prop.default


def test_fbximportoptions_valid_defaults() -> None:
    """It has valid default values."""
    exceptions = {}

    options = mayafbx.FbxImportOptions()
    for prop, _ in options:
        value = exceptions.get(prop.command, prop.get())
        assert value == prop.default


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


def test_export_import_animated_cube(tmp_path: Path) -> None:
    """I can export and import an animated mesh."""
    cube = cmds.polyCube()[0]
    cmds.setKeyframe(f"{cube}.translateX", time=1, value=0)
    cmds.setKeyframe(f"{cube}.translateX", time=24, value=10)
    assert cmds.keyframe(f"{cube}.translateX", query=True, keyframeCount=True) == 2

    options = mayafbx.FbxExportOptions()
    options.animation = True

    filepath = tmp_path / "animated_cube.fbx"
    mayafbx.export_fbx(filepath, options)

    cmds.cutKey(f"{cube}.translateX", option="keys")
    assert cmds.keyframe(f"{cube}.translateX", query=True, keyframeCount=True) == 0

    options = mayafbx.FbxImportOptions()
    options.merge_mode = mayafbx.MergeMode.MERGE
    options.animation = True

    mayafbx.import_fbx(filepath, options)
    assert cmds.keyframe(f"{cube}.translateX", query=True, keyframeCount=True) == 2

    key_values = cmds.keyframe(
        f"{cube}.translateX",
        query=True,
        valueChange=True,
        timeChange=True,
    )
    assert key_values == [1.0, 0.0, 24.0, 10.0]
