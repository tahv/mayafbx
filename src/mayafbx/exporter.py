# ruff:  noqa: E501
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

from maya.api import OpenMaya

from mayafbx.bases import FbxOptions, FbxPropertyField, applied_options
from mayafbx.enums import (
    AxisConversionMethod,
    FileFormat,
    FileVersion,
    NurbsSurfaceAs,
    QuaternionInterpolation,
    UpAxis,
)
from mayafbx.utils import (
    Take,
    get_anim_control_end_time,
    get_anim_control_start_time,
    get_export_takes,
    logger,
    run_mel_command,
    set_export_takes,
)

__all__ = (
    "FbxExportOptions",
    "export_fbx",
    "restore_export_preset",
)


def export_fbx(
    filename: os.PathLike[str],
    options: FbxExportOptions,
    *,
    selection: bool = False,
    takes: list[Take] | None = None,
) -> None:
    """Export to specified `filename` using `options`.

    Args:
        filename: Destination `.fbx` file.
        options: Export options.
        selection: Export only selected elements.
            Default to `False`, which export the whole scene.
        takes: An optional list of animation [Take][mayafbx.Take] to export.

    Raises:
        RuntimeError: If `selection` is `True` but nothing is selected.
    """
    # NOTE: The FBXExport command expects forward slashes `/`
    path = os.path.normpath(filename).replace("\\", "/")
    takes = takes or []

    command = ["FBXExport", "-f", f'"{path}"']
    if selection:
        if OpenMaya.MGlobal.getActiveSelectionList().length() == 0:
            msg = "Nothing Selected."
            raise RuntimeError(msg)
        command += ["-s"]

    with applied_options(options), _applied_export_takes(takes):
        run_mel_command(" ".join(command))

    logger.info("Exported %s to '%s'", "selection" if selection else "scene", path)


def restore_export_preset() -> None:
    """Restores the default values of the FBX Exporter.

    Values are restored by loading the *"Autodesk Media & Entertainment"*
    export preset.
    """
    run_mel_command("FBXResetExport")


@contextmanager
def _applied_export_takes(takes: list[Take]) -> Generator[None, None, None]:
    """Apply export takes during context."""
    backup = get_export_takes()
    set_export_takes(takes)
    yield
    set_export_takes(backup)


class FbxExportOptions(FbxOptions):
    """Wrapper for `FBXProperty Export|*` and `FBXExport*` mel commands.

    The fields documentation are from the official Maya documentation
    for [FBX Export MEL commands](https://help.autodesk.com/view/MAYAUL/2025/ENU/?guid=GUID-6CCE943A-2ED4-4CEE-96D4-9CB19C28F4E0)
    and [FBX Export options](https://help.autodesk.com/view/MAYAUL/2025/ENU/?guid=GUID-FE8DBEAA-C2DD-43B3-9933-4BA4CDDEAA89).
    """

    smoothing_groups = FbxPropertyField(
        command="FBXExportSmoothingGroups",
        type=bool,
        default=False,
    )
    """Converts edge information to Smoothing Groups and export them with the file.

    Mel Command: `FBXExportSmoothingGroups`.
    """

    hard_edges = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|expHardEdges",
        type=bool,
        default=False,
    )
    """Split geometry vertex normals based on edge continuity.

    Vertex normals determine the visual smoothing between polygon faces.
    They reflect how Maya renders the polygons in smooth shaded mode.

    Note:
        This operation duplicates vertex information and converts the geometry.
        Use is to keep the same hard/soft edge look that you get
        from Maya in MotionBuilder.

    Warning:
        Using this option alters UV maps applied to geometry permanently.
        The UVs are then properly reassigned to the newly split geometry.
        When you import this geometry into an empty Maya scene,
        there is a UV limitation where
        using Combine per-vertex Normals in the FBX Importer might result in
        incorrect UV assignments.

    Mel Command: `FBXExportHardEdges`.
    """

    tangents = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|TangentsandBinormals",
        type=bool,
        default=False,
    )
    """Create tangents and binormals data from UV and Normal information of meshes.

    - Your geometry must have UV information.
    - There is a known FBX limitation where exported binormal and/or tangent
      information does not appear, even if you activate this option.
    - This option only works on meshes that have only triangle polygons,
      so you may need to `triangulate` the mesh.

    Mel Command: `FBXExportTangents`.
    """

    smooth_mesh = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|SmoothMesh",
        type=bool,
        default=True,
    )
    """Export source mesh with Smooth mesh attributes.

    To export the source mesh,
    disable the **Smooth mesh Preview** attribute in Maya.

    - If **enabled**, the mesh is not tessellated,
      and the source is exported with Smooth Mesh data.
    - If **disabled**, the mesh is tessellated and exported without Smooth Mesh data.

    Note:
        If you export a Smooth Mesh Preview from Maya
        with the FBX Exporter Smooth Mesh option disabled,
        it will not affect the mesh in the scene.
        Instead your result is a tessellated mesh in the file,
        but with the original source mesh unaffected/unchanged in the Maya scene.

    Mel Command: `FBXExportSmoothMesh`.
    """

    selection_set = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|SelectionSet",
        type=bool,
        default=False,
    )
    """Include Selection Sets.

    Because including Selection Sets can potentially increase the file size,
    this option is disabled by default.
    """

    blind_data = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|BlindData",
        type=bool,
        default=True,
    )
    """Export [Blind data](https://help.autodesk.com/view/MAYAUL/2025/ENU/?guid=GUID-6B2E2B87-C990-416F-B772-D0CED101F5E6)
    stored on polygons.

    Blind data is information stored with polygons which is not used by Maya,
    but might be useful to the platform to which you export to.

    For example, when you use Maya to create content for interactive game levels
    you can use blind data to specify which faces of the level are "solid" or
    "permeable" to the character, or which faces on a polygon mesh are lava and
    hurt the character, and so on.
    """

    convert_to_null = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|AnimationOnly",
        type=bool,
        default=False,
    )
    """Convert all geometry into locators (dummy objects).

    This option is often used for animation only files.
    It creates a smaller file size,
    and is supported by FBX Importer when you import it into the original scene.

    - If you import the file into the original scene,
      the plug-in only imports animation onto the original geometries,
      and does not add incoming Nulls to the existing scene.
    - If you import the file into a new scene,
      the plug-in imports the Nulls with the animation applied.

    Mel Command: `FBXExportAnimationOnly`.
    """

    preserve_instances = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|Instances",
        type=bool,
        default=False,
    )
    """Preserve Maya instances in the FBX export.

    If you disable this option, instances are converted to objects.

    Note:
        The Maya FBX plug-in does not support the duplication of input connections.
        The use of Instances is supported but duplicating the inputs is not.

    Mel Command: `FBXExportInstances`.
    """

    referenced_asset_content = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Geometry|ContainerObjects",
        type=bool,
        default=True,
    )
    """Export referenced [Asset](https://help.autodesk.com/view/MAYAUL/2025/ENU/?guid=GUID-1826F831-E3D1-4045-B6B9-F7D34360C331),
    along with its contents.

    In other words, containers are exported with any data associated with them.
    If you activate this option, your references instead become objects
    in the exported FBX file.

    - You can only use this option when you export an FBX file.
      If you import this file back into Maya,
      the contents of your asset are imported as well.
      Disable this option and the content of the referenced asset is not exported.
    - FBX does not support Assets with transform.
    - Custom attributes on asset nodes are not included when exporting to FBX.

    Mel Command: `FBXExportReferencedContainersContent` in Maya < 2014,
    `FBXExportReferencedAssetsContent` in Maya 2014+.
    """

    triangulate = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|Triangulate",
        type=bool,
        default=False,
    )
    """Tessellates exported polygon geometry.

    This option affects Polygon Meshes, not NURBS.

    Mel Command: `FBXExportTriangulate`.
    """

    convert_nurbs_surface_as = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|GeometryNurbsSurfaceAs",
        type=NurbsSurfaceAs,
        default=NurbsSurfaceAs.NURBS,
    )
    """Convert NURBS geometry into a mesh during the export process.

    Use this option if you are exporting to a software that does not support NURBS.
    """

    animation = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Animation",
        type=bool,
        default=True,
    )
    """Export animation."""

    delete_original_take_on_split_animation = FbxPropertyField(
        command="FBXExportDeleteOriginalTakeOnSplitAnimation",
        type=bool,
        default=False,
    )
    """Remove the default `Take 001` when exporting takes."""

    use_scene_name = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Animation|ExtraGrp|UseSceneName",
        type=bool,
        default=False,
    )
    """Save the scene animation using the scene name as take name.

    Requires [animation][mayafbx.FbxExportOptions.animation].

    If `False`, the plug-in saves Maya scene animation as ``Take 001``.

    Mel Command: `FBXExportUseSceneName`.
    """

    remove_single_key = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Animation|ExtraGrp|RemoveSingleKey",
        type=bool,
        default=False,
    )
    """Removes keys from objects on export if the animation has only one key.

    When two or more keys exist in the file, the keys are exported.

    Requires [animation][mayafbx.FbxExportOptions.animation].

    Note:
        Sometimes, even though objects in a file contain no animation,
        they have a single key assigned to them for use as a locator.
        If you do not need these single keys in your file,
        you can reduce the file size by activating this option to discard them.
    """

    quaternion_interpolation = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Animation|ExtraGrp|Quaternion",
        type=QuaternionInterpolation,
        default=QuaternionInterpolation.RESAMPLE_AS_EULER,
    )
    """How to export quaternion interpolations from the host application.

    Requires [animation][mayafbx.FbxExportOptions.animation].

    Mel Command: `FBXExportQuaternion`.
    """

    bake_complex_animation = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation",
        type=bool,
        default=False,
    )
    """Bakes (plot) all **unsupported** constraints into animation curves.

    You can then import these curves into another application
    that does not support these Maya constraints.

    Requires [animation][mayafbx.FbxExportOptions.animation].

    Note:
        - This option alone won't bake supported animated elements, for a full
          bake you must also set `bake_resample_all` to `True`.
        - By default the plug-in takes the Start and End values automatically
          from Timeline. You can manually set `bake_animation_start`,
          `bake_animation_end` and `bake_animation_step`
          to bake a specific section of time.

    Mel Command: `FBXExportBakeComplexAnimation`.
    """

    bake_animation_start = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStart",
        type=int,
        default=get_anim_control_start_time,
    )
    """Bake start frame.

    Default to the **Animation Start Time** as set in the Ranger Slider UI
    at the time this class was instantiated.

    Requires [animation][mayafbx.FbxExportOptions.animation]
    and [bake_complex_animation][mayafbx.FbxExportOptions.bake_complex_animation].

    Mel Command: `FBXExportBakeComplexStart`.
    """

    bake_animation_end = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameEnd",
        type=int,
        default=get_anim_control_end_time,
    )
    """Bake end frame.

    Default to the **Animation End Time** as set in the Ranger Slider UI
    at the time this class was instantiated.

    Requires [animation][mayafbx.FbxExportOptions.animation]
    and [bake_complex_animation][mayafbx.FbxExportOptions.bake_complex_animation].

    Mel Command: `FBXExportBakeComplexEnd`.
    """

    bake_animation_step = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStep",
        type=int,
        default=1,
    )
    """Bake step frames.

    Setting a step value of 2, for example,
    only bakes and exports a key every other frame.

    Requires [animation][mayafbx.FbxExportOptions.animation]
    and [bake_complex_animation][mayafbx.FbxExportOptions.bake_complex_animation].

    Mel Command: `FBXExportBakeComplexStep`.
    """

    # TODO(tga): Is `bake_resample_all` automatically set to True when
    # `bake_complex_animation` is set to True ?

    bake_resample_all = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|ResampleAnimationCurves",
        type=bool,
        default=False,
    )
    """Bake even the **supported** animated elements.

    This is unlike
    [bake_complex_animation][mayafbx.FbxExportOptions.bake_complex_animation]
    which selectively bakes unsupported elements only.

    Requires [animation][mayafbx.FbxExportOptions.animation].

    See [constraints][mayafbx.FbxExportOptions.constraints]
    for a list of supported constraints elements.

    Mel Command: `FBXExportBakeResampleAnimation`.
    """

    deformation = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|Deformation",
        type=bool,
        default=True,
    )
    """Export Skin and Blend Shape deformations.

    You can choose to export Skins and Bend Shapes specifically with
    [deformation_skins][mayafbx.FbxExportOptions.deformation_skins]
    and [deformation_shapes][mayafbx.FbxExportOptions.deformation_shapes].
    """

    deformation_skins = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|Deformation|Skins",
        type=bool,
        default=True,
    )
    """Export skin deformation.

    Require [deformation][mayafbx.FbxExportOptions.deformation].

    Mel Command: `FBXExportSkins`.
    """

    deformation_shapes = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|Deformation|Shape",
        type=bool,
        default=True,
    )
    """Export Blend Shapes.

    Require [deformation][mayafbx.FbxExportOptions.deformation].

    Mel Command: `FBXExportShapes`.
    """

    # TODO(tga): ShapeAttributes have been added in FBX SDK 2020:
    # The FbxShape class has been expanded to handle more channels
    # (BiNormals, VertexColor and UV) called "Modern Style".
    # See the class documentation and the ShapeAttributes sample code
    # for more information.
    # TODO(tga): deformation_shape_attributes = FbxPropertyField("FBXProperty Export|IncludeGrp|Animation|Deformation|ShapeAttributes", type=bool, default=False)
    # TODO(tga): deformation_shape_attributes_values = FbxPropertyField("FBXProperty Export|IncludeGrp|Animation|Deformation|ShapeAttributes|ShapeAttributesValues", type=str, default="Relative")  # ["Relative" "Absolute"]

    curve_filter = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|CurveFilter",
        type=bool,
        default=False,
    )
    """Apply filters to animation curves during the export process."""

    constant_key_reducer = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed",
        type=bool,
        default=False,
    )
    """Remove redundant keys.

    Redundant keys are keys that have the same value, which are equivalent to
    flat horizontal interpolations on a curve.
    This helps to reduce the size of resampled curves, especially Scale.

    Setting this to `False` ensures that the animation data is not filtered.

    You can set specific thresholds for each type of transform:

    - [constant_key_reducer_translation_precision][mayafbx.FbxExportOptions.constant_key_reducer_translation_precision]
    - [constant_key_reducer_rotation_precision][mayafbx.FbxExportOptions.constant_key_reducer_rotation_precision]
    - [constant_key_reducer_scale_precision][mayafbx.FbxExportOptions.constant_key_reducer_scale_precision]
    - [constant_key_reducer_other_precision][mayafbx.FbxExportOptions.constant_key_reducer_other_precision]

    Requires [curve_filter][mayafbx.FbxExportOptions.curve_filter].

    Mel Command: `FBXExportApplyConstantKeyReducer`.
    """

    constant_key_reducer_translation_precision = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedTPrec",
        type=float,
        default=0.0001,
    )
    """Threshold for translation curves in generic units.

    Requires [constant_key_reducer][mayafbx.FbxExportOptions.constant_key_reducer].
    """

    constant_key_reducer_rotation_precision = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedRPrec",
        type=float,
        default=0.009,
    )
    """Threshold for rotation curves in generic units.

    Requires [constant_key_reducer][mayafbx.FbxExportOptions.constant_key_reducer].
    """

    constant_key_reducer_scale_precision = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedSPrec",
        type=float,
        default=0.004,
    )
    """Threshold for scaling curves in generic units.

    Requires [constant_key_reducer][mayafbx.FbxExportOptions.constant_key_reducer].
    """

    constant_key_reducer_other_precision = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedOPrec",
        default=0.009,
        type=float,
    )
    """Threshold for other curves in generic units.

    Other includes transforms like Blend Shapes and custom attribute curves.

    Requires [constant_key_reducer][mayafbx.FbxExportOptions.constant_key_reducer].
    """

    constant_key_reducer_auto_tangents_only = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|AutoTangentsOnly",
        type=bool,
        default=True,
    )
    """Only filter ``auto`` key type.

    When `False`, keys with interpolation values greater than a certain threshold
    may get deleted.

    Requires [constant_key_reducer][mayafbx.FbxExportOptions.constant_key_reducer].

    Note:
        The Maya FBX plug-in converts all animation keys to User,
        which is not an Auto tangent.
        To ensure that constant key reducing occurs, set this to ``False``.
    """

    point_cache = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|PointCache",
        type=bool,
        default=False,
    )
    """Create a geometry cache file of a chosen selection set.

    To use this option, create a selection set of the objects for which
    you want to retain the vertex animation.
    You must apply the set to the Objects Transform node and not the Shape node.
    By default, any Geometry cache files created are in .MCX format.

    When you activate this option, three files (`FBX`, `XML` and `MCX`) are generated.

    The Maya FBX plug-in stores the XML and MCX files in a subfolder
    named after the FBX file and has the suffix `_fpc`.

    Use [selection_set_name_as_point_cache][mayafbx.FbxExportOptions.selection_set_name_as_point_cache]
    to select an appropriate set to export.

    Mel Command: `FBXExportCacheFile`.
    """

    selection_set_name_as_point_cache = FbxPropertyField(
        "FBXExportQuickSelectSetAsCache",
        type=str,
        default=" ",
    )
    """The set to be used when exporting the cache file.

    This command does not validate the received string.
    However, if the string used here does not correspond to
    an existing (and valid) set in the Maya scene, the cache export fails.

    Requires [point_cache][mayafbx.FbxExportOptions.point_cache].

    Mel Command: `FBXExportQuickSelectSetAsCache`.
    """

    constraints = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|ConstraintsGrp|Constraint",
        type=bool,
        default=False,
    )
    """Export supported constraints.

    FBX support the following constraints:

    - Point
    - Aim
    - Orient
    - Parent
    - IK handle (including Pole vector)

    Export your constraints effectively without the need to bake the animation first,
    if you are transferring to a package that which supports these constraints,
    like MotionBuilder.

    Mel Command: `FBXExportConstraints`.

    Note:
        If you export your scene with the intention of importing it
        into a package that does not support these constraints (such as 3ds Max),
        bake the animation first.
        See [bake_complex_animation][mayafbx.FbxExportOptions.bake_complex_animation]
        and [bake_resample_all][mayafbx.FbxExportOptions.bake_resample_all]
        for more information.
    """

    skeleton_definition = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|ConstraintsGrp|Character",
        type=bool,
        default=False,
    )
    """Include Skeleton definitions (FBIK/HumanIK).

    Useful if you are transferring to MotionBuilder, which also support Characters.

    Mel Command: `FBXExportCharacter` in Maya < 2013,
    `FBXExportSkeletonDefinitions` in Maya 2013+.
    """

    cameras = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|CameraGrp|Camera",
        type=bool,
        default=True,
    )
    """Export cameras.

    The Maya FBX plug-in exports camera settings,
    but not render settings associated to the camera with the file.
    This can change rendering results depending on the source application
    used in comparison.

    During the export, Maya cameras are converted into FBX camera types
    for interoperability.

    Question: Why are cameras inconsistent ?
        - If you import a Maya camera into 3ds Max using a
          Fit Resolution Gate setting of Vertical or Fill,
          the results will differ.
        - For better support between Maya cameras in 3ds Max,
          set the Fit Resolution Gate setting to Horizontal,
          rather than Vertical or the default, Fill.

    Mel Command: `FBXExportCameras`.
    """

    lights = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|LightGrp|Light",
        type=bool,
        default=True,
    )
    """Export lights.

    The Maya FBX plug-in exports and converts light types to ensure interoperability.

    FBX supports Point, Spot and Directional lights types.

    Mel Command: `FBXExportLights`.
    """

    audio = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Audio",
        type=bool,
        default=True,
    )
    """Export audio.

    The data itself are the Audio clips and tracks found in the Time Editor.

    Only the active composition is processed during export.
    """

    embed_media = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|EmbedTextureGrp|EmbedTexture",
        type=bool,
        default=False,
    )
    """Include (embed) media (textures, for example) within the FBX file.

    Embed your media to ensure that all your textures are carried over and loaded
    when you open the FBX file on another computer.

    Warning:
        Since this media is contained within the FBX file itself,
        this has an impact on file size.
        Therefore, use this option only when you transport an FBX file
        to a location where the original media source
        is no longer accessible by the receiver.

    When you import an FBX file with embedded media,
    the embedded files extract to a `<fileName>.fbm` folder
    in the same location as the FBX file.

    If you do not have write permission to create that new folder,
    the media files are Imported to the user's temp folder,
    such as `C:\\Documents and Settings\\<username>\\Local Settings\\Temp`.

    If disabled, the Maya FBX plug-in stores the relative and absolute paths
    of the associated media files at export time.
    This causes problems if, for some reason, the path is no longer accessible.
    Make sure that the associated media is accessible to ensure
    the proper import of these media files.

    Mel Command: `FBXExportEmbeddedTextures`.
    """

    bind_pose = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|BindPose",
        type=bool,
        default=True,
    )
    """Export characters bind poses."""

    # TODO(tga): documentation
    pivot_to_nulls = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|PivotToNulls",
        type=bool,
        default=False,
    )

    bypass_rrs_inheritance = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|BypassRrsInheritance",
        type=bool,
        default=False,
    )
    """Bypass Rrs inheritance.

    FBX File format supports three different types of transformation inheritance:

    - `eInheritRrSs`: Scaling of parent is applied in the child world
      after the local child rotation.
    - `eInheritRSrs`: Scaling of parent is applied in the parent world.
    - `eInheritRrs`: Scaling of parent does not affect the scaling of children.

    `Rrs` stands for `ParentRotate * ChildRotate * ChildScale`
    and is the mode of inheritance used by joint hierarchy in Maya, also known as
    **Segment Scale Compensate**.

    For more information, see the section *FBX and scale compensation*
    in [FBX Limitations](https://help.autodesk.com/view/MAYAUL/2025/ENU/?guid=GUID-AA3B8EA4-DDFB-4B0F-9654-2BF6B8781AE7),
    [Computing transformation matrices](https://help.autodesk.com/view/FBX/2020/ENU/?guid=FBX_Developer_Help_nodes_and_scene_graph_fbx_nodes_computing_transformation_matrix_html)
    and [facebookincubator/FBX2glTF/#27](https://github.com/facebookincubator/FBX2glTF/issues/27#issuecomment-340110562).
    """

    include_children = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|InputConnectionsGrp|IncludeChildren",
        type=bool,
        default=True,
    )
    """Include the hierarchy below the selected objects when exporting selection.

    The `selection` parameter of [export_fbx](mayafbx.export_fbx) must be `True`.

    Mel Command: `FBXExportIncludeChildren`.
    """

    input_connections = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|InputConnectionsGrp|InputConnections",
        type=bool,
        default=True,
    )
    """Include all related input connections when exporting selection.

    The `selection` parameter of [export_fbx](mayafbx.export_fbx) must be `True`.

    Mel Command: `FBXExportInputConnections`.
    """

    automatic_units = FbxPropertyField(
        "FBXProperty Export|AdvOptGrp|UnitsGrp|DynamicScaleConversion",
        default=True,
        type=bool,
    )
    """Automatically set the units of the exported file to match the units of the scene.

    If `True`, the plug-in applies no conversion (scale factor of `1.0`).

    If you apply this option,
    the [convert_units_to][mayafbx.FbxExportOptions.convert_units_to]
    option won't have any effect.
    """

    up_axis = FbxPropertyField(
        "FBXProperty Export|AdvOptGrp|AxisConvGrp|UpAxis",
        type=UpAxis,
        default=UpAxis.from_scene,
    )
    """Up axis conversion.

    Default to the the **Scene Up Axis** as set in
    `Window > Settings/Preferences > Preferences > Settings`.

    - Only applies axis conversion to the root elements of the scene.
    - If you have animation on a root object that must be converted on
      export, these animation curves are resampled to apply the proper axis
      conversion.
    - To avoid resampling these animation curves, make sure to add a Root
      Node (dummy object) as a parent of the animated object in your scene,
      before you export to FBX.

    Mel Command: `FBXExportUpAxis`.
    """

    axis_conversion_method = FbxPropertyField(
        "FBXExportAxisConversionMethod",
        type=AxisConversionMethod,
        default=AxisConversionMethod.CONVERT_ANIMATION,
    )
    """Set an export conversion method.

    Mel Command: `FBXExportAxisConversionMethod`.
    """

    show_warning_ui = FbxPropertyField(
        "FBXProperty Export|AdvOptGrp|UI|ShowWarningsManager",
        default=True,
        type=bool,
    )
    """Show the Warning Manager dialog if something unexpected occurs during the export."""

    generate_log = FbxPropertyField(
        "FBXProperty Export|AdvOptGrp|UI|GenerateLogData",
        default=True,
        type=bool,
    )
    """Generate log data.

    The Maya FBX plug-in stores log files with the FBX presets,
    in ``C:\\My Documents\\Maya\\FBX\\Logs``.

    Mel Command: `FBXExportGenerateLog`.
    """

    file_format = FbxPropertyField(
        "FBXProperty Export|AdvOptGrp|Fbx|AsciiFbx",
        type=FileFormat,
        default=FileFormat.BINARY,
    )
    """Save file in Binary or ASCII.

    Mel Command: `FBXExportInAscii`, which is a `bool`.
    """

    file_version = FbxPropertyField(
        "FBXExportFileVersion",
        # "FBXProperty Export|AdvOptGrp|Fbx|ExportFileVersion",
        type=str,
        default=FileVersion.current_value,
    )
    """Specify an FBX version to use for export.

    Change this option when you want to import your file using an older plug-in
    version, where the source and destination plug-in versions do not match.

    Default to plugin value.

    If your version is missing from [FileVersion](mayafbx.FileVersion),
    set the value as a `str`.

    Mel Command: `FBXExportFileVersion`.
    """
