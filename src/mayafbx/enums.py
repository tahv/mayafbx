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
    "QuaternionInterpolation",
]


class NurbsSurfaceAs(StrEnum):
    """Supported nurbs surfaces conversions on export."""

    NURBS = "NURBS"
    """No conversion applied, NURBS geometry is exported as NURBS."""

    INTERACTIVE_DISPLAY_MESH = "Interactive Display Mesh"
    """Converts geometry based on the NURBS display settings."""

    SOFTWARE_RENDER_MESH = "Software Render Mesh"
    """Converts geometry based on the NURBS render settings."""


class QuaternionInterpolation(StrEnum):
    """How to handle quaternion interpolation on import/export."""

    RESAMPLE_AS_EULER = "Resample As Euler Interpolation"  # "resample"
    """Converts and resamples quaternion interpolations into Euler curves.

    Use this option to obtain visual results identical to your animation in
    MotionBuilder or other applications.
    """

    RETAIN_QUATERNION = "Retain Quaternion Interpolation"  # "quaternion"
    """Retains quaternion interpolation types during the export process.

    Use this option when you export animation that has quaternion interpolations.

    Note:
        - This option is only compatible with applications supporting this
          interpolation type, such as Autodesk MotionBuilder.
        - The resulting animation will not be identical since
          quaternion evaluations are different in Maya and MotionBuilder.
    """

    SET_AS_EULER = "Set As Euler Interpolation"  # "euler"
    """Changes the interpolation type of quaternion keys to a Euler type,
    without resampling the animation curves themselves.

    Note:
        - Using this option results in the same number of keys, set as Euler
          types.
        - The visual result will be different since it is now evaluated as a
          Euler interpolation.
    """
