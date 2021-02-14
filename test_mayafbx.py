from __future__ import division, absolute_import, print_function

import pytest
import itertools

from maya import mel

import mayafbx

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Helpers


def bool_get(command):
    raw_value = mel.eval(' '.join([command, '-q']))
    return {'true': True, 'false': False}.get(raw_value, bool(raw_value))


def bool_set(command, value):
    mel.eval(' '.join([command, "-v", str(value).lower()]))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Tests


def test_from_scene():
    command = "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups"

    bool_set(command, True)
    options = mayafbx.FbxExportOptions.from_scene()
    assert options.smoothing_groups == bool_get(command)

    bool_set(command, False)
    options = mayafbx.FbxExportOptions.from_scene()
    assert options.smoothing_groups == bool_get(command)


def test_set_value():
    options = mayafbx.FbxExportOptions()
    options.smoothing_groups = False
    assert options.smoothing_groups is False
    options.smoothing_groups = True
    assert options.smoothing_groups is True


def test_apply():
    command = "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups"
    options = mayafbx.FbxExportOptions()

    options.smoothing_groups = True
    options.apply()
    assert bool_get(command) is True

    options.smoothing_groups = False
    options.apply()
    assert bool_get(command) is False


def test_as_context():
    command = "FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups"

    options = mayafbx.FbxExportOptions()
    options.smoothing_groups = False

    bool_set(command, True)
    with options:
        print(options.smoothing_groups)
        assert bool_get(command) is False
    assert bool_get(command) is True


def test_setitem():
    option = mayafbx.FbxExportOptions()

    option['smoothing_groups'] = False
    assert option.smoothing_groups is False

    option['smoothing_groups'] = True
    assert option.smoothing_groups is True


def test_getitem():
    option = mayafbx.FbxExportOptions()

    option.smoothing_groups = False
    assert option['smoothing_groups'] is False

    option.smoothing_groups = True
    assert option['smoothing_groups'] is True


def test_init_kwargs():
    options = mayafbx.FbxExportOptions(smoothing_groups=False)
    assert options.smoothing_groups is False
    options = mayafbx.FbxExportOptions(smoothing_groups=True)
    assert options.smoothing_groups is True


def test_raise_setitem():
    option = mayafbx.FbxExportOptions()
    with pytest.raises(KeyError):
        option['invalid'] = False


def test_raise_getitem():
    option = mayafbx.FbxExportOptions()
    with pytest.raises(KeyError):
        option['invalid']


def test_unique_command():
    # Detect typo during dev.
    visited = {}  # {"command": [property_names]}

    properties = itertools.chain(
        mayafbx.FbxExportOptions()._properties().items(),
        mayafbx.FbxImportOptions()._properties().items())

    for name, prop in properties:
        visited.setdefault(prop.command, []).append(name)

    issues = [
        "{} : {}".format(command, names)
        for command, names in visited.items()
        if len(names) > 1]

    assert not issues, "\n".join(["Non unique commands:"] + issues)


def test_query_all():
    for options in (mayafbx.FbxExportOptions, mayafbx.FbxImportOptions):
        options = options()
        for name in options._properties().keys():
            getattr(options, name)
