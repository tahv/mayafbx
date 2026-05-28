from __future__ import annotations

import os

from mayafbx.bases import FbxOptions, FbxPropertyField, applied_options, run_mel_command
from mayafbx.enums import (
    ConvertUnit,
    ForcedFileAxis,
    MergeMode,
    QuaternionInterpolation,
    SamplingRate,
    SkeletonDefinition,
    UpAxis,
)
from mayafbx.utils import logger

__all__ = (
    "FbxImportOptions",
    "import_fbx",
    "restore_import_preset",
)


def import_fbx(
    filename: os.PathLike[str],
    options: FbxImportOptions,
    *,
    take: int | None = None,
) -> None:
    """Import `filename` using `options`.

    Args:
        filename: Path to a `.fbx` file.
        options: Import options.
        take: Specify the appropriate take number to load the corresponding take.
            If you specify `0`, the plugin imports no animation.
            If you specify `-1`, the plugin retrieves the last take in the take array.
            The plugin considers any number of takes greater than
            the amount of takes contained in the file
            or any negative value less than `-1` to be invalid.
    """
    # NOTE: The FBXImport command only accept '/'
    path = os.path.normpath(filename).replace("\\", "/")

    command = ["FBXImport", "-f", f'"{path}"']
    if take is not None:
        command += ["-t", f"{take}"]

    with applied_options(options):
        run_mel_command(" ".join(command))

    logger.info("Imported '%s' to scene", path)


def restore_import_preset() -> None:
    """Restores the default values of the FBX Importer.

    Values are restored by loading the *"Autodesk Media & Entertainment"* import preset.
    """
    run_mel_command("FBXResetImport")


class FbxImportOptions(FbxOptions):
    """Wrapper for `FBXProperty Import|*` and `FBXImport*` mel commands.

    The fields documentation are from the official Maya documentation
    for [FBX Import MEL commands](https://help.autodesk.com/view/MAYAUL/2025/ENU/?guid=GUID-699CDF74-3D64-44B0-967E-7427DF800290)
    and [FBX Import options](https://help.autodesk.com/view/MAYAUL/2025/ENU/?guid=GUID-0CD41066-4C27-48AE-9776-366DB11B4FDF)
    """

    merge_mode = FbxPropertyField(
        "FBXImportMode",
        type=MergeMode,
        default=MergeMode.MERGE,
    )
    """How to import the content of your file into the host application.

    Mel Command: `FBXImportMode`.
    """

    smoothing_groups = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Geometry|SmoothingGroups",
        type=bool,
        default=False,
        available=(2024, None),
    )
    """Import Smoothing Groups.

    Added in Maya 2024.

    FBX polygon objects with smooth edge normals will reimport into Maya
    with incorrect normal information unless you activate
    [FbxExportOptions.smoothing_groups][mayafbx.FbxExportOptions.smoothing_groups]
    on export, and this option on import.
    """

    unlock_normals = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Geometry|UnlockNormals",
        type=bool,
        default=False,
    )
    """Recomputes the normals on the objects using Maya internal algorithms.

    - Normals are automatically unlocked for all deformed geometry imported into Maya.
    - Locked normals can create shading issues for geometry if a deformer is
      applied after import. Unlocking geometry normals resolves this.

    Mel Command: `FBXImportUnlockNormals`.
    """

    hard_edges = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Geometry|HardEdges",
        type=bool,
        default=False,
    )
    """Combine geometry vertex Normals.

    Merges back all vertices located at the same exact position as a unique vertex.
    The Maya FBX plug-in then determines if the edges connected to each
    vertex are hard edges or smooth edges, based on their normals.

    Use this when [FbxExportOptions.hard_edges][mayafbx.FbxExportOptions.hard_edges]
    was set to `True` on export.

    - Using this option permanently alters any UV maps applied to geometry.
    - The plug-in properly re-assigns the UVs to the newly split geometry.
    - There is a limitation in regards to UVs, when importing this geometry
      into an empty Maya scene, as it may result in incorrect UV assignments.

    Mel Command: `FBXImportHardEdges`.
    """

    blind_data = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Geometry|BlindData",
        type=bool,
        default=True,
    )
    """Import Blind Data stored on polygons.

    Blind data is information stored with polygons which is not used by Maya,
    but might be useful to the platform to which you export to.

    See [FbxExportOptions.blind_data][mayafbx.FbxExportOptions.blind_data]
    for more information.
    """

    remove_bad_polys = FbxPropertyField(
        "FBXProperty Import|AdvOptGrp|Performance|RemoveBadPolysFromMesh",
        default=True,
        type=bool,
    )
    """Remove degenerate polygons from the mesh object.

    Remove two-sided polygons, single vertex polygons, and so on.
    """

    animation = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation",
        default=True,
        type=bool,
    )
    """Import animation."""

    # TODO(tga): the fill_timeline options is overridden by Maya ?
    fill_timeline = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|TimeLine",
        type=bool,
        default=False,
    )
    """Update the application timeline by the animation range in the incoming FBX file.

    Mel Command: `FBXImportFillTimeline`.
    """

    bake_animation_layers = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|BakeAnimationLayers",
        default=True,
        type=bool,
    )
    """Bake (plot) animation layers contained in the incoming file.

    If you disable this option, all the layers in the FBX file will be imported.

    Mel Command: `FBXImportMergeAnimationLayers`.
    """

    optical_markers = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|Markers",
        default=False,
        type=bool,
    )
    """Import optical markers contained in the file as dummy objects.

    If disabled, the import process ignores this data.

    Optical markers normally come from motion capture data, as a cloud of
    animated points or markers.
    The Maya FBX plug-in does not import the animation as the data type is incompatible.
    However, the Maya FBX plug-in converts optical data into a cloud of
    static null objects in Maya.

    Note:
        If your optical data originates from MotionBuilder, you can set the
        state of all optical markers to `Done` in MotionBuilder which lets you
        import the animation data as curves in Maya.
    """

    quaternion_interpolation = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|Quaternion",
        type=str,
        default=QuaternionInterpolation.RESAMPLE_AS_EULER,
    )
    """Convert and resample quaternion interpolation into Euler curves.

    Compensates differences between Maya and MotionBuilder quaternions.

    Mel Command: `FBXImportQuaternion`.
    """

    protect_driven_keys = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|ProtectDrivenKeys",
        type=bool,
        default=False,
    )
    """Prevent any incoming animation from overwriting channels with driven keys.

    Maya has special driven keys that link one attribute value to another
    object attribute.
    These keys are exclusive to Maya and are not supported by FBX.
    When this option is active, the Maya FBX plug-in prevents the disconnection
    or overwrite of attributes that use driven keys.

    - If `True`, the driven keys are protected and no incoming animation
      is applied to the driven channels.
    - If `False`, the driven keys are discarded and the incoming animation
      is applied to the driven channels.

    Mel Command: `FBXImportProtectDrivenKeys`.
    """

    deforming_elements_to_joint = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|DeformNullsAsJoints",
        type=bool,
        default=True,
    )
    """Convert deforming elements into Maya joints.

    If `False`, elements other than joints being used to deform are converted
    to locators.

    Note:
        This option was originally provided because Maya did not support locator
        elements (transform nodes that are not joints) within a bone hierarchy.
        While Maya now supports this, in some cases this option improves the
        skinning behavior.
    """

    update_pivots_from_nulls = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|NullsToPivot",
        type=bool,
        default=True,
    )
    """Assign the rotation transformation of the null (or joints) elements in
    the hierarchy that are used as pre- and post-rotation to the joint orient
    and the rotate axis of the original node.

    The look-up is done by name
    as the pre-rotation node's name contains the `__Pre_` suffix,
    while the post-rotation node's name has a `__Post_` suffix.

    Activate this option when you import older (pre-MotionBuilder 5.5)
    FBX files that contain an animated joint hierarchy,
    for example, an animated character.

    Note:
        When [merge_mode][FbxImportOptions.merge_mode] is set to
        [MergeMode.UPDATE_ANIMATION][mayafbx.MergeMode.UPDATE_ANIMATION]
        or [MergeMode.MERGE][mayafbx.MergeMode.MERGE]
        this option is automatically set to `True`.

    Mel Command: `FBXImportMergeBackNullPivots`
    """

    point_cache = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|ExtraGrp|PointCache",
        type=bool,
        default=True,
    )
    """Import FBX-exported geometry cache data during the FBX import process.

    The Maya FBX plug-in generates three files when you export Geometry cache files
    using FBX: an FBX, XML and MCX file.

    The plug-in stores XML and MCX files in a subfolder named after the FBX file
    and has the suffix FPC (`_fpc`).

    Mel Command: `FBXImportCacheFile`.
    """

    deformation = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|Deformation",
        type=bool,
        default=True,
    )
    """Import Skin and Blend Shape deformatons."""

    deformaton_skins = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|Deformation|Skins",
        type=bool,
        default=True,
    )
    """Import Skinning.

    Requires [deformation][mayafbx.FbxImportOptions.deformation].

    Mel Command: `FBXImportSkins`.
    """

    deformation_shapes = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|Deformation|Shape",
        type=bool,
        default=True,
    )
    """Import Blend Shapes.

    Requires [deformation][mayafbx.FbxImportOptions.deformation].

    Mel Command: `FBXImportShapes`.
    """

    deformation_normalize_weights = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|Deformation|ForceWeightNormalize",
        type=bool,
        default=False,
    )
    """Normalize weight assignment.

    Pre-Normalize weights to ensure that every vertex on a skinned mesh has a
    weight no less than a total of `1.0`.

    You can have many joints that influence a single vertex, however, the
    percentage of each deforming joint always equals a sum total of `1.0`.

    Requires [deformation][mayafbx.FbxImportOptions.deformation].
    """

    keep_attributes_locked = FbxPropertyField(
        "FBXImportSetLockedAttribute",
        type=bool,
        default=False,
    )
    """Unlock channels in Maya that contain animation in incoming FBX.

    Use when you import an FBX file that contains animation onto an object that
    has locked channels.
    """

    sampling_rate = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|SamplingPanel|SamplingRateSelector",
        type=SamplingRate,
        default=SamplingRate.SCENE,
    )
    """The source used by the plugin to resample keyframes data.

    Mel Command: `FBXImportResamplingRateSource`
    """

    set_maya_framerate = FbxPropertyField(
        "FBXImportSetMayaFrameRate",
        type=bool,
        default=False,
    )
    """Overwrite Maya frame rate with incoming FBX frame rate.

    Mel Command: `FBXImportSetMayaFrameRate`.
    """

    custom_sampling_rate = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|SamplingPanel|CurveFilterSamplingRate",
        type=float,
        default=30.0,
    )
    """Custom rate to resample keyframes data.

    Only evaluated if [sampling_rate][mayafbx.FbxExportOptions.sampling_rate]
    is [SamplingRate.CUSTOM][mayafbx.SamplingRate.CUSTOM].
    """

    # TODO(tga): documentation
    curve_filter = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|CurveFilter",
        type=bool,
        default=False,
    )

    constraints = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|ConstraintsGrp|Constraint",
        type=bool,
        default=True,
    )
    """Import supported constraints contained in the FBX file to Maya.

    FBX support the following constraints:

    - Point
    - Aim
    - Orient
    - Parent,
    - IK handle (including Pole vector)

    Mel Command: `FBXImportConstraints`.
    """

    skeleton_definition = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Animation|ConstraintsGrp|CharacterType",
        default=SkeletonDefinition.HUMAN_IK,
        type=SkeletonDefinition,
    )
    """Select the Skeleton definition to use on import.

    Useful if you are importing from MotionBuilder, which supports characters.

    Mel Command: `FBXImportSkeletonType`.
    """

    cameras = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|CameraGrp|Camera",
        type=bool,
        default=True,
    )
    """Import cameras.

    Mel Command: `FBXImportCameras`.
    """

    lights = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|LightGrp|Light",
        type=bool,
        default=True,
    )
    """bool: Import lights.

    FBX supports Point, Spot and Directional lights types.

    Mel Command: `FBXImportLights`.
    """

    audio = FbxPropertyField(
        "FBXProperty Import|IncludeGrp|Audio",
        type=bool,
        default=True,
    )
    """Import audio."""

    automatic_units = FbxPropertyField(
        "FBXProperty Import|AdvOptGrp|UnitsGrp|DynamicScaleConversion",
        type=bool,
        default=True,
    )
    """Automatically identify and convert units of the incoming file
    to match the units of the scene.

    - This conversion affects only incoming data.
    - This does not change the settings in Maya.
    """

    convert_units_to = FbxPropertyField(
        "FBXProperty Import|AdvOptGrp|UnitsGrp|UnitsSelector",
        type=ConvertUnit,
        default=ConvertUnit.from_scene,
    )
    """Specify the units to which you want to convert the incoming data.

    Affects the Scale Factor value applied to the imported data.

    Default to the Maya System Units,
    as set in `Window > Settings/Preferences > Preferences > Settings`.

    Only evaluated if [automatic_units][mayafbx.FbxImportOptions.automatic_units]
    is `False`.
    """

    axis_conversion = FbxPropertyField(
        "FBXProperty Import|AdvOptGrp|AxisConvGrp|AxisConversion",
        type=bool,
        default=False,
    )
    """Enable axis conversion on import.

    Mel Command: `FBXImportAxisConversionEnable`.
    """

    up_axis = FbxPropertyField(
        "FBXProperty Import|AdvOptGrp|AxisConvGrp|UpAxis",
        type=str,
        default=UpAxis.from_scene,
    )
    """Up axis conversion.

    Default to the the scene up axis,
    as set in `Window > Settings/Preferences > Preferences > Settings`.

    Only evaluated if [axis_conversion][mayafbx.FbxImportOptions.axis_conversion]
    is `True`.

    - Only applies axis conversion to the root elements of the incoming scene.
    - If you have animation on a root object that must be converted on import,
      these animation curves are resampled to apply the proper axis conversion.

    Mel Command: `FBXImportUpAxis`.
    """

    forced_file_axis = FbxPropertyField(
        "FBXImportForcedFileAxis",
        type=str,
        default=ForcedFileAxis.DISABLED,
    )
    """*Force* the FBX plug-in to consider the data in the file
    as if it is natively generated with the specified axis.

    Mel Command: `FBXImportForcedFileAxis`.
    """

    show_warning_ui = FbxPropertyField(
        "FBXProperty Import|AdvOptGrp|UI|ShowWarningsManager",
        type=bool,
        default=True,
    )
    """Show the Warning Manager dialog if something unexpected occurs during import."""

    generate_log = FbxPropertyField(
        "FBXProperty Import|AdvOptGrp|UI|GenerateLogData",
        type=bool,
        default=True,
    )
    """Generate log data.

    The Maya FBX plug-in stores log files with the FBX presets,
    in `C:\\My Documents\\Maya\\FBX\\Logs`.

    Mel Command: `FBXImportGenerateLog`.
    """
