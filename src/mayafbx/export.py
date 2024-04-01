from mayafbx.bases import FbxOptions, FbxPropertyField

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
        Your geometry must have UV information.

    Note:
        There is a known FBX limitation where exported binormal and/or tangent 
        information does not appear, even if you activate this option.

        This option only works on meshes that have only triangle polygons,
        so you may need to `.triangulate` the mesh.

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
