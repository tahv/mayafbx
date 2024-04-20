"""Export FBX."""

from __future__ import annotations

import os

from maya.api import OpenMaya

from mayafbx.bases import FbxOptions, FbxPropertyField, applied_options
from mayafbx.enums import (
    AxisConversionMethod,
    ConvertUnit,
    FileFormat,
    FileVersion,
    NurbsSurfaceAs,
    QuaternionInterpolation,
    UpAxis,
)
from mayafbx.utils import (
    get_anim_control_end_time,
    get_anim_control_start_time,
    logger,
    run_mel_command,
)

__all__ = [
    "export_fbx",
    "restore_export_preset",
    "FbxExportOptions",
]

# TODO: investigate undocumented option: FbxExportDeleteOriginalTakeOnSplitAnimation
# https://discourse.techart.online/t/maya-fbx-take-export/11321

# TODO: investigate command: FBXExportSplitAnimationIntoTakes

def export_fbx(
    filename: os.PathLike,
    options: FbxExportOptions,
    *,
    selection: bool = False,
) -> None:
    """Export to specified ``filename`` location using ``options``.

    Args:
        filename: Destination ``.fbx`` file.
        options: Export options.
        selection: Export only selected elements.
            Default to `False`, which export the whole scene.

    Raises:
        RuntimeError: If ``selection`` is `True` and nothing is selected.
    """
    # NOTE: The FBXExport command only accept '/'
    path = os.path.normpath(filename).replace("\\", "/")

    command = ["FBXExport", "-f", f'"{path}"']
    if selection:
        if OpenMaya.MGlobal.getActiveSelectionList().length() == 0:
            msg = "Nothing Selected."
            raise RuntimeError(msg)
        command += ["-s"]

    with applied_options(options):
        run_mel_command(" ".join(command))

    logger.info("Exported %s to '%s'", "selection" if selection else "scene", path)


def restore_export_preset() -> None:
    """Restores the default values of the FBX Exporter.

    Values are restored by loading the "Autodesk Media & Entertainment" export preset.
    """
    run_mel_command("FBXResetExport")


class FbxExportOptions(FbxOptions):
    """Wrapper for ``FBXProperty Export|...`` and ``FBXExport...`` mel commands.

    The fields documentation are from the official Maya documentation
    for `FBX Export MEL commands`_ and `FBX Export options`_.
    """

    smoothing_groups = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|SmoothingGroups",
        type=bool,
        default=False,
    )
    """Converts edge information to Smoothing Groups and export them with the file.

    Default to `False`.

    Mel Command:
        ``FBXExportSmoothingGroups``
    """

    hard_edges = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|expHardEdges",
        type=bool,
        default=False,
    )
    """Split geometry vertex normals based on edge continuity.

    Vertex normals determine the visual smoothing between polygon faces.
    They reflect how Maya renders the polygons in smooth shaded mode.

    Default to `False`.

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

    Mel Command:
        ``FBXExportHardEdges``
    """

    tangents = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|TangentsandBinormals",
        type=bool,
        default=False,
    )
    """Create tangents and binormals data from UV and Normal information of meshes.

    Default to `False`.

    Note:
        - Your geometry must have UV information.
        - There is a known FBX limitation where exported binormal and/or tangent 
          information does not appear, even if you activate this option.
        - This option only works on meshes that have only triangle polygons,
          so you may need to `triangulate` the mesh.

    Mel Command:
        ``FBXExportTangents``
    """

    smooth_mesh = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|SmoothMesh",
        type=bool,
        default=True,
    )
    """Export source mesh with Smooth mesh attributes.

    To export the source mesh, disable the Smooth mesh Preview attribute in Maya.

    If you **activate** the Smooth Mesh option,
    the mesh is not tessellated, and the source is exported with Smooth Mesh data.

    If you **disable** the Smooth Mesh option,
    the mesh is tessellated and exported without Smooth Mesh data.

    Default to `True`.

    Note:
        If you export a Smooth Mesh Preview from Maya
        with the FBX Exporter Smooth Mesh option disabled,
        it will not affect the mesh in the scene.
        Instead your result is a tessellated mesh in the file,
        but with the original source mesh unaffected/unchanged in the Maya scene.

    Mel Command:
        ``FBXExportSmoothMesh``
    """

    selection_set = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|SelectionSet",
        type=bool,
        default=False,
    )
    """Include Selection Sets.

    Because including Selection Sets can potentially increase the file size,
    this option is disabled by default.

    Default to `False`.
    """

    blind_data = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|BlindData",
        type=bool,
        default=True,
    )
    """Export `Blind data`_ stored on polygons.

    Blind data is information stored with polygons which is not used by Maya,
    but might be useful to the platform to which you export to.

    For example, when you use Maya to create content for interactive game levels
    you can use blind data to specify which faces of the level are "solid" or
    "permeable" to the character, or which faces on a polygon mesh are lava and
    hurt the character, and so on.

    Default to `True`.

    .. _Blind data:
        https://help.autodesk.com/view/MAYAUL/2025/ENU/?guid=GUID-6B2E2B87-C990-416F-B772-D0CED101F5E6
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

    Default to `False`.

    Note:
        - If you import the file into the original scene,
          the plug-in only imports animation onto the original geometries,
          and does not add incoming Nulls to the existing scene.
        - If you import the file into a new scene,
          the plug-in imports the Nulls with the animation applied.

    Mel Command:
        ``FBXExportAnimationOnly``
    """

    preserve_instances = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|Instances",
        type=bool,
        default=False,
    )
    """Preserve Maya instances in the FBX export

    If you disable this option, instances are converted to objects.

    Default to `False`.

    Note:
        The Maya FBX plug-in does not support the duplication of input connections.
        The use of Instances is supported but duplicating the inputs is not.

    Mel Command:
        ``FBXExportInstances``
    """

    referenced_asset_content = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Geometry|ContainerObjects",
        type=bool,
        default=True,
    )
    """Export referenced asset, along with its contents.

    In other words, containers are exported with any data associated with them.
    If you activate this option, your references instead become objects
    in the exported FBX file.

    Note:
        - You can only use this option when you export an FBX file. 
          If you import this file back into Maya,
          the contents of your asset are imported as well.
          Disable this option and the content of the referenced asset is not exported.
        - FBX does not support Assets with transform.
        - Custom attributes on asset nodes are not included when exporting to FBX.

    For more information about assets, see `Assets`_.

    Mel Command:
        ``FBXExportReferencedContainersContent`` in Maya < 2014.

        ``FBXExportReferencedAssetsContent`` in Maya >= 2014.

    .. _Assets:
        https://help.autodesk.com/view/MAYAUL/2025/ENU/?guid=GUID-1826F831-E3D1-4045-B6B9-F7D34360C331
    """

    triangulate = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|Triangulate",
        type=bool,
        default=False,
    )
    """Tessellates exported polygon geometry.

    Default to `False`.

    Note:
        This option affects Polygon Meshes, not NURBS.

    Mel Command:
        ``FBXExportTriangulate``
    """

    convert_nurbs_surface_as = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Geometry|GeometryNurbsSurfaceAs",
        type=NurbsSurfaceAs,
        default=NurbsSurfaceAs.NURBS,
    )
    """Convert NURBS geometry into a mesh during the export process.

    Use this option if you are exporting to a software that does not support
    NURBS.

    Default to `NurbsSurfaceAs.NURBS`.

    See `NurbsSurfaceAs` for possible values.
    """

    animation = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Animation",
        type=bool,
        default=True,
    )
    """Export animation.

    Default to `True`.
    """

    use_scene_name = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Animation|ExtraGrp|UseSceneName",
        type=bool,
        default=False,
    )
    """Save the scene animation using the scene name as take name.

    If `False`, the plug-in saves Maya scene animation as ``Take 001``.

    Default to `False`.

    Require `animation`.

    Mel Command:
        ``FBXExportUseSceneName``
    """

    remove_single_key = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Animation|ExtraGrp|RemoveSingleKey",
        type=bool,
        default=False,
    )
    """Removes keys from objects on export if the animation has only one key.

    When two or more keys exist in the file, the keys are exported.

    Note:
        Sometimes, even though objects in a file contain no animation,
        they have a single key assigned to them for use as a locator.
        If you do not need these single keys in your file,
        you can reduce the file size by activating this option to discard them.

    Default to `False`.

    Require `animation`.
    """

    quaternion_interpolation = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Animation|ExtraGrp|Quaternion",
        type=QuaternionInterpolation,
        default=QuaternionInterpolation.RESAMPLE_AS_EULER,
    )
    """How to export quaternion interpolations from the host application.

    Default to `QuaternionInterpolation.RESAMPLE_AS_EULER`.

    See `QuaternionInterpolation` for possible values.

    Require `animation`.

    Mel Command:
        ``FBXExportQuaternion``
    """

    bake_complexe_animation = FbxPropertyField(
        command="FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation",
        type=bool,
        default=False,
    )
    """Bakes (plot) all **unsupported** constraints into animation curves.

    You can then import these curves into another application
    that does not support these Maya constraints.

    Note:
        - This option alone won't bake supported animated elements, for a full
          bake you must also set `bake_resample_all` to `True`.
        - By default the plug-in takes the Start and End values automatically
          from Timeline. You can manually set `bake_animation_start`,
          `bake_animation_end` and `bake_animation_step`
          to bake a specific section of time.

    Default to `False`.

    Require `animation`.

    Mel Command:
        ``FBXExportBakeComplexAnimation``
    """

    bake_animation_start = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStart",
        type=int,
        default=get_anim_control_start_time,
    )
    """Bake start frame.

    Default to the **Animation Start Time** as set in the Ranger Slider UI
    at the time this class was instanciated.

    Require `bake_complexe_animation`.

    Mel Command:
        ``FBXExportBakeComplexStart``
    """

    bake_animation_end = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameEnd",
        type=int,
        default=get_anim_control_end_time,
    )
    """Bake end frame.

    Default to the **Animation End Time** as set in the Ranger Slider UI
    at the time this class was instanciated.

    Require `bake_complexe_animation`.

    Mel Command:
        ``FBXExportBakeComplexEnd``
    """

    bake_animation_step = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|BakeFrameStep",
        type=int,
        default=1,
    )
    """Bake step frames.

    Setting a Step value of 2 for example, only bakes and exports a key every
    other frame.

    Default to ``1``.

    Require `bake_complexe_animation`.

    Mel Command:
        ``FBXExportBakeComplexStep``
    """

    # TODO: Is `bake_resample_all` automatically set to True when
    # `bake_complexe_animation` is set to True ?

    bake_resample_all = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|ResampleAnimationCurves",  # noqa: E501
        type=bool,
        default=False,
    )
    """Bake even the **supported** animated elements.

    This is unlike `bake_complexe_animation`
    which selectively bakes unsupported elements only.

    Default to `False`.

    Require `animation`.

    See `constraints` for a list of supported constraints elements.

    Mel Command:
        ``FBXExportBakeResampleAnimation``
    """

    # # TODO:
    # hide_bake_warnings = FbxPropertyField(
    #     "FBXProperty Export|IncludeGrp|Animation|BakeComplexAnimation|HideComplexAnimationBakedWarning",
    #     type=bool,
    #     default=False,
    # )

    deformation = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|Deformation",
        type=bool,
        default=True,
    )
    """Export Skin and Blend Shape deformations.

    You can choose to export Skins and Bend Shapes specifically with 
    `deformation_skins` and `deformation_shapes`.

    Default to `True`.
    """

    deformation_skins = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|Deformation|Skins",
        type=bool,
        default=True,
    )
    """Export skin deformation.

    Default to `True`.

    Require `deformation`.

    Mel Command:
        ``FBXExportSkins``
    """

    deformation_shapes = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|Deformation|Shape",
        type=bool,
        default=True,
    )
    """Export Blend Shapes.

    Default to `True`.

    Require `deformation`.

    Mel Command:
        ``FBXExportShapes``
    """

    # TODO: ShapeAttribues have been added in FBX SDK 2020:
    # The FbxShape class has been expanded to handle more channels
    # (BiNormals, VertexColor and UV) called "Modern Style".
    # See the class documentation and the ShapeAttributes sample code
    # for more information.

    # deformation_shape_attributes = FbxPropertyField(
    #     "FBXProperty Export|IncludeGrp|Animation|Deformation|ShapeAttributes",
    #     type=bool,
    #     default=False,
    # )
    #
    # deformation_shape_attributes_values = FbxPropertyField(
    #     "FBXProperty Export|IncludeGrp|Animation|Deformation|ShapeAttributes|ShapeAttributesValues",
    #     type=str,
    #     default="Relative",  # ["Relative" "Absolute"]
    # )

    curve_filter = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|CurveFilter",
        type=bool,
        default=False,
    )
    """Apply filters to animation curves during the export process.

    Default to `False`.
    """

    constant_key_reducer = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed",
        type=bool,
        default=False,
    )
    """Remove redundant keys.

    Redundant keys are keys that have the same value, which are equivalent to
    flat horizontal interpolations on a curve.

    This helps to reduce the size of resampled curves, especially Scale.

    Setting this to ``False`` ensures that the animation data is not filtered.

    You can set specific thresholds for each type of transform:
        - `constant_key_reducer_translation_precision`
        - `constant_key_reducer_rotation_precision`
        - `constant_key_reducer_scale_precision`
        - `constant_key_reducer_other_precision`

    Default to `False`.

    Require `curve_filter`.

    Mel Command:
        ``FBXExportApplyConstantKeyReducer``
    """

    constant_key_reducer_translation_precision = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedTPrec",  # noqa: E501
        type=float,
        default=0.0001,
    )
    """Threshold for translation curves in generic units.

    Default to ``0.0001``.

    Require `constant_key_reducer`.
    """

    constant_key_reducer_rotation_precision = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedRPrec",  # noqa: E501
        type=float,
        default=0.009,
    )
    """Threshold for rotation curves in generic units.

    Default to ``0.009``.

    Require `constant_key_reducer`.
    """

    constant_key_reducer_scale_precision = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedSPrec",  # noqa: E501
        type=float,
        default=0.004,
    )
    """Threshold for scaling curves in generic units.

    Default to ``0.004``.

    Require `constant_key_reducer`.
    """

    constant_key_reducer_other_precision = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|CurveFilterCstKeyRedOPrec",  # noqa: E501
        default=0.009,
        type=float,
    )
    """Threshold for other curves in generic units.

    Other includes transforms like Blend Shapes and custom attribute curves.

    Default to ``0.009``.

    Require `constant_key_reducer`.
    """

    constant_key_reducer_auto_tangents_only = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|CurveFilter|CurveFilterApplyCstKeyRed|AutoTangentsOnly",  # noqa: E501
        type=bool,
        default=True,
    )
    """Only filter ``auto`` key type.

    When `False`, keys with interpolation values greater than a certain threshold
    may get deleted.

    Default to `True`.

    Require `constant_key_reducer`.

    Note:
        The Maya FBX plug-in converts all animation keys to User,
        which is not an Auto tangent.
        To ensure that constant key reducing occurs, set this to ``False``.
    """

    # TODO: point_cache
    # point_cache = FbxPropertyField(
    #     "FBXProperty Export|IncludeGrp|Animation|PointCache",
    #     default=False,
    #     type=bool,
    # )  # "FBXExportCacheFile"

    # TODO: selection_set_name_as_point_cache
    # selection_set_name_as_point_cache = FbxPropertyField(
    #     "FBXProperty Export|IncludeGrp|Animation|PointCache|SelectionSetNameAsPointCache",
    #     default="",
    #     type=str,
    # )  # "FBXExportQuickSelectSetAsCache"

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

    Note:
        If you export your scene with the intention of importing it
        into a package that does not support these constraints (such as 3ds Max),
        bake the animation first.
        See `bake_complexe_animation` and `bake_resample_all` for more information.

    Default to `False`.

    Mel Command:
        ``FBXExportConstraints``
    """

    skeleton_definition = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Animation|ConstraintsGrp|Character",
        type=bool,
        default=False,
    )
    """Include Skeleton definitions (FBIK/HumanIK).

    Useful if you are transferring to MotionBuilder, which also support Characters.

    Default to `False`.

    Mel Command:
        ``FBXExportCharacter`` in Maya < 2013.

        ``FBXExportSkeletonDefinitions`` in Maya >= 2013.
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

    Note:
        During the export, Maya cameras are converted into FBX camera types
        for interoperability.

    .. admonition:: Why are my cameras inconsistent ?
        :class: warning

        - If you import a Maya camera into 3ds Max using a
          Fit Resolution Gate setting of Vertical or Fill,
          the results will differ.
        - For better support between Maya cameras in 3ds Max,
          set the Fit Resolution Gate setting to Horizontal,
          rather than Vertical or the default, Fill.

    Default to `True`.

    Mel Command:
        ``FBXExportCameras``
    """

    lights = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|LightGrp|Light",
        type=bool,
        default=True,
    )
    """Export lights.

    Note:
        The Maya FBX plug-in exports and converts light types
        to ensure interoperability.

    FBX support the following lights types:
        - Point
        - Spot
        - Directional

    Default to `True`.

    Mel Command:
        ``FBXExportLights``
    """

    audio = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|Audio",
        type=bool,
        default=True,
    )
    """Export audio.

    Note:
        - The data itself are the Audio clips and tracks found in the Time Editor.
        - Only the active composition is processed during export.

    Default to `True`.
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

    Note:
        - When you import an FBX file with embedded media,
          the embedded files extract to a ``<fileName>.fbm`` folder
          in the same location as the FBX file.
        - If you do not have write permission to create that new folder,
          the media files are Imported to the user's temp folder,
          such as ``C:\\Documents and Settings\\<username>\\Local Settings\\Temp``.

    If disabled, the Maya FBX plug-in stores the relative and absolute paths
    of the associated media files at export time.
    This causes problems if, for some reason, the path is no longer accessible.
    Make sure that the associated media is accessible to ensure
    the proper import of these media files.

    Default to `False`.

    Mel Command:
        ``FBXExportEmbeddedTextures``
    """

    bind_pose = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|BindPose",
        type=bool,
        default=True,
    )
    """Export characters bind poses.

    Default to `True`.
    """

    # TODO: documentation
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
        - ``eInheritRrSs``: Scaling of parent is applied in the child world after
          the local child rotation.
        - ``eInheritRSrs``: Scaling of parent is applied in the parent world.
        - ``eInheritRrs``: Scaling of parent does not affect the scaling of children.

    ``Rrs`` stands for ``ParentRotate * ChildRotate * ChildScale``
    and is the mode of inheritance used by joint hierarchy in Maya, also known as
    **Segment Scale Compensate**.

    For more information, see `FBX and scale compensation`_,
    `Computing transformation matrices`_ and this
    `github comment <https://github.com/facebookincubator/FBX2glTF/issues/27#issuecomment-340110562>`_.

    .. _FBX and scale compensation:
        https://help.autodesk.com/view/MAYAUL/2025/ENU/?guid=GUID-AA3B8EA4-DDFB-4B0F-9654-2BF6B8781AE7#GUID-AA3B8EA4-DDFB-4B0F-9654-2BF6B8781AE7__GUID-0604653D-C49F-47C4-8387-652D331F7F09

    .. _Computing transformation matrices:
        https://help.autodesk.com/view/FBX/2020/ENU/?guid=FBX_Developer_Help_nodes_and_scene_graph_fbx_nodes_computing_transformation_matrix_html
    """

    include_children = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|InputConnectionsGrp|IncludeChildren",
        type=bool,
        default=True,
    )
    """Include the hierarchy below the selected objects when exporting selection.

    Default to `True`.

    The ``selection`` parameter of `export_fbx` must be ``True``.

    Mel Command:
        ``FBXExportIncludeChildren``
    """

    input_connections = FbxPropertyField(
        "FBXProperty Export|IncludeGrp|InputConnectionsGrp|InputConnections",
        type=bool,
        default=True,
    )
    """Include all related input connections when exporting selection.

    Default to `True`.

    The ``selection`` parameter of `export_fbx` must be ``True``.

    Mel Command:
        ``FBXExportInputConnections``
    """

    automatic_units = FbxPropertyField(
        "FBXProperty Export|AdvOptGrp|UnitsGrp|DynamicScaleConversion",
        default=True,
        type=bool,
    )
    """Automatically set the units of the exported file to match the units of the scene.

    If `True`, the plug-in applies no conversion (scale factor of 1.0).

    If you apply this option, the `convert_units_to` option won't have any effect.

    Default to `True`.
    """

    # TODO: "FBXExportScaleFactor" (float) is only queryable, create get_export_scale_factor ?

    convert_units_to = FbxPropertyField(
        # "FBXProperty Export|AdvOptGrp|UnitsGrp|UnitsSelector",
        "FBXExportConvertUnitString",
        type=ConvertUnit,
        default=ConvertUnit.from_scene,
    )
    """Specify the units to which you want to convert your exported scene.

    This settings affects the **Scale Factor** value applied to the exported data.

    Default to the **Maya System Units** as set in
    ``Window > Settings/Preferences > Preferences > Settings``.

    Only evaluated if `automatic_units` is `False`.

    See `ConvertUnit` for possible values.

    Mel Command:
        ``FBXExportConvertUnitString``
    """

    up_axis = FbxPropertyField(
        "FBXProperty Export|AdvOptGrp|AxisConvGrp|UpAxis",
        type=UpAxis,
        default=UpAxis.from_scene,
    )
    """Up axis conversion.

    Default to the the **Scene Up Axis** as set in
    ``Window > Settings/Preferences > Preferences > Settings``.

    See `UpAxis` for possible values.

    Note:
        - Only applies axis conversion to the root elements of the scene.
        - If you have animation on a root object that must be converted on
          export, these animation curves are resampled to apply the proper axis
          conversion.
        - To avoid resampling these animation curves, make sure to add a Root
          Node (dummy object) as a parent of the animated object in your scene,
          before you export to FBX.

    Mel Command:
        ``FBXExportUpAxis``
    """

    axis_conversion_method = FbxPropertyField(
        "FBXExportAxisConversionMethod",
        type=AxisConversionMethod,
        default=AxisConversionMethod.CONVERT_ANIMATION,
    )
    """Set an export conversion method.

    Default to `AxisConversionMethod.CONVERT_ANIMATION`.

    See `AxisConversionMethod` for possible values.

    Mel Command:
        ``FBXExportAxisConversionMethod``
    """

    show_warning_ui = FbxPropertyField(
        "FBXProperty Export|AdvOptGrp|UI|ShowWarningsManager",
        default=True,
        type=bool,
    )
    """Show the Warning Manager dialog if something unexpected occurs during the export.

    Default to `True`.
    """

    generate_log = FbxPropertyField(
        "FBXProperty Export|AdvOptGrp|UI|GenerateLogData",
        default=True,
        type=bool,
    )
    """Generate log data.

    The Maya FBX plug-in stores log files with the FBX presets, 
    in ``C:\\My Documents\\Maya\\FBX\\Logs``.

    Default to `True`.

    Mel Command:
        ``FBXExportGenerateLog``
    """

    file_format = FbxPropertyField(
        "FBXProperty Export|AdvOptGrp|Fbx|AsciiFbx",
        type=FileFormat,
        default=FileFormat.BINARY,
    )
    """Save file in Binary or ASCII.

    Default to `FileFormat.BINARY`.

    See `FileFormat` for possible values.

    Mel Command:
        ``FBXExportInAscii``, which is a `bool`.
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

    See `FileVersion` for possible values. You set the value as a `str` if
    your version is missing from the enum.

    Mel Command:
        ``FBXExportFileVersion``
    """

    # TODO "FBXExportSplitAnimationIntoTakes"


"""
TODO: The following properties are not implemented:

Export|AdvOptGrp|FileFormat|Obj|Triangulate - Bool - True
Export|AdvOptGrp|FileFormat|Obj|Deformation - Bool - True
Export|AdvOptGrp|FileFormat|Motion_Base|MotionFrameCount - Integer - 0
Export|AdvOptGrp|FileFormat|Motion_Base|MotionFromGlobalPosition - Bool - True
Export|AdvOptGrp|FileFormat|Motion_Base|MotionFrameRate - Number - 30.000000
Export|AdvOptGrp|FileFormat|Motion_Base|MotionGapsAsValidData - Bool - False
Export|AdvOptGrp|FileFormat|Motion_Base|MotionC3DRealFormat - Bool - False
Export|AdvOptGrp|FileFormat|Motion_Base|MotionASFSceneOwned - Bool - True
Export|AdvOptGrp|FileFormat|Biovision_BVH|MotionTranslation - Bool - True
Export|AdvOptGrp|FileFormat|Acclaim_ASF|MotionTranslation - Bool - True
Export|AdvOptGrp|FileFormat|Acclaim_ASF|MotionFrameRateUsed - Bool - True
Export|AdvOptGrp|FileFormat|Acclaim_ASF|MotionFrameRange - Bool - True
Export|AdvOptGrp|FileFormat|Acclaim_ASF|MotionWriteDefaultAsBaseTR - Bool - False
Export|AdvOptGrp|FileFormat|Acclaim_AMC|MotionTranslation - Bool - True
Export|AdvOptGrp|FileFormat|Acclaim_AMC|MotionFrameRateUsed - Bool - True
Export|AdvOptGrp|FileFormat|Acclaim_AMC|MotionFrameRange - Bool - True
Export|AdvOptGrp|FileFormat|Acclaim_AMC|MotionWriteDefaultAsBaseTR - Bool - False
Export|AdvOptGrp|Dxf|Deformation - Bool - True  - FBXExportDxfTriangulate
Export|AdvOptGrp|Dxf|Triangulate - Bool - True  - FBXExportDxfDeformation
Export|AdvOptGrp|Collada|Triangulate - Bool - True  - FBXExportColladaTriangulate
Export|AdvOptGrp|Collada|SingleMatrix - Bool - True  - FBXExportColladaSingleMatrix
Export|AdvOptGrp|Collada|FrameRate - Number - 24.000000 - FBXExportColladaFrameRate
"""
