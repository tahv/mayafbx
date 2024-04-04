from mayafbx.bases import FbxOptions, FbxPropertyField
from mayafbx.enums import NurbsSurfaceAs, QuaternionInterpolation

__all__ = [
    "FbxExportOptions",
]


class FbxExportOptions(FbxOptions):
    """Wrapper for ``FBXProperty Export|...`` and ``FBXExport...`` mel commands.

    The fields documentation are from the official Maya documentation
    for `FBX Export MEL commands`_ and `FBX Export options`_.
    """

    smoothing_group = FbxPropertyField(
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

    tangent = FbxPropertyField(
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

    # TODO
    # referenced_asset_content = FbxPropertyField(
    #     command="FBXProperty Export|IncludeGrp|Geometry|ContainerObjects",
    #     # "FBXExportReferencedContainersContent" if VERSION < 2014 else "FBXExportReferencedAssetsContent"
    #     type=bool,
    #     default=True,
    # )

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

    Default to `QuaternionInterpolation.kResampleAsEuler`.

    See `QuaternionInterpolation` for possible values.

    Require `animation`.

    Mel Command:
        ``FBXExportQuaternion``
    """
