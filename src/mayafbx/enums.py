"""Package enums."""

from __future__ import annotations

import sys

from maya.api import OpenMaya

from mayafbx.utils import run_mel_command

if sys.version_info < (3, 11):
    from enum import Enum

    class StrEnum(str, Enum):
        """StrEnum is a Python `enum.Enum` that inherits from `str`."""

        def __str__(self) -> str:
            return str(self.value)
else:
    from enum import StrEnum

__all__ = [
    "NurbsSurfaceAs",
]


class NurbsSurfaceAs(StrEnum):
    """Supported nurbs surfaces conversions on export."""

    NURBS = "NURBS"
    """No conversion applied, NURBS geometry is exported as NURBS."""

    INTERACTIVE_DISPLAY_MESH = "Interactive Display Mesh"
    """Converts geometry based on the NURBS display settings."""

    SOFTWARE_RENDER_MESH = "Software Render Mesh"
    """Converts geometry based on the NURBS render settings."""
