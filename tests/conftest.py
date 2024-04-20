from typing import Generator

import pytest


@pytest.fixture(scope="session", autouse=True)
def initialize_maya() -> Generator[None, None, None]:
    import maya.standalone

    maya.standalone.initialize()
    from maya import cmds

    cmds.loadPlugin("fbxmaya")

    yield

    maya.standalone.uninitialize()
