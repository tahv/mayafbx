"""Package enums."""

from __future__ import annotations

import sys

from maya.api import OpenMaya

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
    "ConvertUnit",
    "UpAxis",
    "AxisConversionMethod",
    "FileFormat",
    "FileVersion",
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


class ConvertUnit(StrEnum):
    """Supported units, change the scale factor on import/export."""

    MILLIMETERS = "mm"  # "Millimeters"
    CENTIMETERS = "cm"  # "Centimeters"
    DECIMETERS = "dm"  # "Decimeters"
    METERS = "m"  # "Meters"
    KILOMETERS = "km"  # "Kilometers"
    INCHES = "In"  # "Inches"
    FEET = "ft"  # "Feet"
    YARDS = "yd"  # "Yards"
    MILES = "mi"  # "Miles"

    @staticmethod
    def from_scene() -> ConvertUnit:
        """Current Maya UI Unit.

        As set in ``Window > Settings/Preferences > Preferences > Settings``.
        """
        return {
            OpenMaya.MDistance.kMillimeters: ConvertUnit.MILLIMETERS,
            OpenMaya.MDistance.kCentimeters: ConvertUnit.CENTIMETERS,
            # NOTE: 'OpenMaya.MDistance.kDecimeters' doesn't exists
            OpenMaya.MDistance.kMeters: ConvertUnit.METERS,
            OpenMaya.MDistance.kKilometers: ConvertUnit.KILOMETERS,
            OpenMaya.MDistance.kInches: ConvertUnit.INCHES,
            OpenMaya.MDistance.kFeet: ConvertUnit.FEET,
            OpenMaya.MDistance.kYards: ConvertUnit.YARDS,
            OpenMaya.MDistance.kMiles: ConvertUnit.MILES,
        }[OpenMaya.MDistance.uiUnit()]


class UpAxis(StrEnum):
    """Supported Up Axis conversions."""

    Y = "Y"
    Z = "Z"

    @staticmethod
    def from_scene() -> UpAxis:
        """Scene up axis."""
        if OpenMaya.MGlobal.isYAxisUp():
            return UpAxis.Y
        if OpenMaya.MGlobal.iZAxisUp():
            return UpAxis.Z
        message = f"Unsupported scene up axis: {OpenMaya.MGlobal.upAxis()}"
        raise RuntimeError(message)


class AxisConversionMethod(StrEnum):
    """Supported axis conversions methods."""

    NONE = "none"
    """No conversion takes place and the exported data is unaffected."""

    CONVERT_ANIMATION = "convertAnimation"
    """Recalculates all animation curves so their values reflect the new World system.
    """

    ADD_ROOT = "addFbxRoot"
    """Adds a transformation node to the top of the scene.

    The node contain the transformations needed to transport the data into
    the new World system.

    Note:
        If the plug-in does not detect a need for the conversion, 
        no ``Fbx_Root`` node is added.
    """


class FileFormat(StrEnum):
    """Supported export file formats."""

    BINARY = "Binary"
    """Standard format."""

    ASCII = "ASCII"
    """Plain text format."""


class FileVersion(StrEnum):
    """Supported file version."""

    FBX_2020 = "FBX202000"
    FBX_2019 = "FBX201900"
    FBX_2018 = "FBX201800"
    FBX_2016 = "FBX201600"
    FBX_2014 = "FBX201400"
    FBX_2013 = "FBX201300"
    FBX_2012 = "FBX201200"
    FBX_2011 = "FBX201100"
    FBX_2010 = "FBX201000"
    FBX_2009 = "FBX200900"
    FBX_2006 = "FBX200611"

    @staticmethod
    def current_value() -> FileVersion:
        """Export version currently used by the plugin."""
        # TODO: improve to get the real default value from Maya preset.
        return mel.eval("FBXExportFileVersion -q")
