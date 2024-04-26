"""Pytest configuration."""
from typing import Generator

import pytest


@pytest.fixture(scope="session", autouse=True)
def initialize_maya_and_fbx() -> Generator[None, None, None]:
    """Initialize Maya standalone and load fbx plugin."""
    import maya.standalone

    maya.standalone.initialize()
    from maya import cmds

    cmds.loadPlugin("fbxmaya")

    yield

    maya.standalone.uninitialize()


@pytest.fixture(autouse=True)
def reset_scene_and_fbx() -> None:
    """Create a new file and restore default FBX options before each test."""
    from maya import cmds, mel

    cmds.file(new=True, force=True)
    mel.eval("FBXResetExport")
    mel.eval("FBXResetImport")
