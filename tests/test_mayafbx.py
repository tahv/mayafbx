"""Test suite for the mayafbx package."""

import mayafbx
from maya import mel
from mayafbx.utils import get_anim_control_end_time


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

    exceptions = {
    }

    options = mayafbx.FbxImportOptions()
    for prop, _ in options:
        value = exceptions.get(prop.command, prop.get())
        assert value == prop.default
