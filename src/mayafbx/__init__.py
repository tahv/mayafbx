"""Python wrapper for the FBX plugin of Maya."""

from mayafbx.enums import (
    AxisConversionMethod,
    FileFormat,
    FileVersion,
    ForcedFileAxis,
    MergeMode,
    NurbsSurfaceAs,
    QuaternionInterpolation,
    SamplingRate,
    SkeletonDefinition,
    UpAxis,
)
from mayafbx.exporter import (
    FbxExportOptions,
    export_fbx,
    restore_export_preset,
)
from mayafbx.importer import (
    FbxImportOptions,
    import_fbx,
    restore_import_preset,
)
from mayafbx.utils import Take, get_scale_factor

__all__ = (
    "AxisConversionMethod",
    "FbxExportOptions",
    "FbxImportOptions",
    "FileFormat",
    "FileVersion",
    "ForcedFileAxis",
    "MergeMode",
    "NurbsSurfaceAs",
    "QuaternionInterpolation",
    "SamplingRate",
    "SkeletonDefinition",
    "Take",
    "UpAxis",
    "export_fbx",
    "get_scale_factor",
    "import_fbx",
    "restore_export_preset",
    "restore_import_preset",
)
