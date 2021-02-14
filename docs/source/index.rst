.. mayafbx documentation master file, created by
   sphinx-quickstart on Fri Jan 22 22:17:17 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

mayafbx
=======

`Github <https://github.com/tahv/mayafbx>`_

.. automodule:: mayafbx

|

Maya Documentation:
    - `FBX Import MEL commands <https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2020/ENU/Maya-DataExchange/files/GUID-699CDF74-3D64-44B0-967E-7427DF800290-htm.html>`_
    - `FBX Import options <https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2020/ENU/Maya-DataExchange/files/GUID-0CD41066-4C27-48AE-9776-366DB11B4FDF-htm.html>`_
    - `FBX Export MEL commands <https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2020/ENU/Maya-DataExchange/files/GUID-6CCE943A-2ED4-4CEE-96D4-9CB19C28F4E0-htm.html>`_
    - `FBX Export options <https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2020/ENU/Maya-DataExchange/files/GUID-FE8DBEAA-C2DD-43B3-9933-4BA4CDDEAA89-htm.html>`_
    - `FBX Limitations <https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2020/ENU/Maya-DataExchange/files/GUID-AA3B8EA4-DDFB-4B0F-9654-2BF6B8781AE7-htm.html>`_
    - `FBX Troubleshooting <https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2020/ENU/Maya-DataExchange/files/GUID-0B2C4423-D37D-4BFC-BC17-DD871FB2AD9A-htm.html>`_

|

Content
=======

Export

.. autosummary::
    :nosignatures:

    mayafbx.FbxExportOptions
    mayafbx.export_fbx
    mayafbx.restore_export_preset

Import

.. autosummary::
    :nosignatures:

    mayafbx.FbxImportOptions
    mayafbx.import_fbx
    mayafbx.restore_import_preset

Enums

.. autosummary::
    :nosignatures:

    mayafbx.QuaternionInterpolation
    mayafbx.ConvertUnit
    mayafbx.UpAxis
    mayafbx.ForcedFileAxis
    mayafbx.AxisConversionMethod
    mayafbx.NurbsSurfaceAs
    mayafbx.FileFormat
    mayafbx.FileVersion
    mayafbx.SkeletonDefinition
    mayafbx.MergeMode
    mayafbx.SamplingRate

|
|

Export
======

.. autofunction:: mayafbx.export_fbx
.. autofunction:: mayafbx.restore_export_preset

|

Export Options
--------------

.. autoclass:: mayafbx::FbxExportOptions

|

.. automethod:: mayafbx::FbxExportOptions.from_scene
.. automethod:: mayafbx::FbxExportOptions.apply

|

Geometry
^^^^^^^^

.. autoattribute:: mayafbx.FbxExportOptions.smoothing_groups
.. autoattribute:: mayafbx.FbxExportOptions.hard_edges
.. autoattribute:: mayafbx.FbxExportOptions.tangents
.. autoattribute:: mayafbx.FbxExportOptions.smooth_mesh
.. autoattribute:: mayafbx.FbxExportOptions.selection_set
.. autoattribute:: mayafbx.FbxExportOptions.blind_data
.. autoattribute:: mayafbx.FbxExportOptions.convert_to_null
.. autoattribute:: mayafbx.FbxExportOptions.preserve_instances
.. autoattribute:: mayafbx.FbxExportOptions.triangulate
.. autoattribute:: mayafbx.FbxExportOptions.convert_nurbs_surface_as

|

Animation
^^^^^^^^^

.. autoattribute:: mayafbx.FbxExportOptions.animation
.. autoattribute:: mayafbx.FbxExportOptions.use_scene_name
.. autoattribute:: mayafbx.FbxExportOptions.remove_single_key
.. autoattribute:: mayafbx.FbxExportOptions.quaternion_interpolation

|

.. autoattribute:: mayafbx.FbxExportOptions.bake_animation
.. autoattribute:: mayafbx.FbxExportOptions.bake_resample_all
.. autoattribute:: mayafbx.FbxExportOptions.bake_animation_start
.. autoattribute:: mayafbx.FbxExportOptions.bake_animation_end
.. autoattribute:: mayafbx.FbxExportOptions.bake_animation_step

|

.. autoattribute:: mayafbx.FbxExportOptions.deformation
.. autoattribute:: mayafbx.FbxExportOptions.deformation_shapes
.. autoattribute:: mayafbx.FbxExportOptions.deformation_skins

|

.. autoattribute:: mayafbx.FbxExportOptions.curve_filter
.. autoattribute:: mayafbx.FbxExportOptions.curve_filter_constant_key_reducer
.. autoattribute:: mayafbx.FbxExportOptions.curve_filter_precision_translation
.. autoattribute:: mayafbx.FbxExportOptions.curve_filter_precision_rotation
.. autoattribute:: mayafbx.FbxExportOptions.curve_filter_precision_scale
.. autoattribute:: mayafbx.FbxExportOptions.curve_filter_precision_other
.. autoattribute:: mayafbx.FbxExportOptions.curve_filter_auto_tangents_only

|

Include
^^^^^^^

.. autoattribute:: mayafbx.FbxExportOptions.constraints
.. autoattribute:: mayafbx.FbxExportOptions.skeleton_definition
.. autoattribute:: mayafbx.FbxExportOptions.cameras
.. autoattribute:: mayafbx.FbxExportOptions.lights
.. autoattribute:: mayafbx.FbxExportOptions.audio
.. autoattribute:: mayafbx.FbxExportOptions.embed_media
.. autoattribute:: mayafbx.FbxExportOptions.bind_pose

|

Selection
^^^^^^^^^

.. autoattribute:: mayafbx.FbxExportOptions.selected
.. autoattribute:: mayafbx.FbxExportOptions.selected_hierarchy
.. autoattribute:: mayafbx.FbxExportOptions.selected_input_connections

|

Advanced
^^^^^^^^

.. autoattribute:: mayafbx.FbxExportOptions.automatic_units
.. autoattribute:: mayafbx.FbxExportOptions.convert_units_to
.. autoattribute:: mayafbx.FbxExportOptions.up_axis
.. autoattribute:: mayafbx.FbxExportOptions.axis_conversion_method
.. autoattribute:: mayafbx.FbxExportOptions.show_warning_ui
.. autoattribute:: mayafbx.FbxExportOptions.generate_log
.. autoattribute:: mayafbx.FbxExportOptions.file_format
.. autoattribute:: mayafbx.FbxExportOptions.file_version

|

--------------------

Import
======

.. autofunction:: mayafbx.import_fbx
.. autofunction:: mayafbx.restore_import_preset

|

Import Options
--------------

.. autoclass:: mayafbx::FbxImportOptions

|

.. automethod:: mayafbx::FbxImportOptions.from_scene
.. automethod:: mayafbx::FbxImportOptions.apply

|

.. autoattribute:: mayafbx.FbxImportOptions.merge_mode

|

Geometry
^^^^^^^^

.. autoattribute:: mayafbx.FbxImportOptions.unlock_normals
.. autoattribute:: mayafbx.FbxImportOptions.hard_edges
.. autoattribute:: mayafbx.FbxImportOptions.blind_data
.. autoattribute:: mayafbx.FbxImportOptions.remove_bad_polys

|

Animation
^^^^^^^^^

.. autoattribute:: mayafbx.FbxImportOptions.animation
.. autoattribute:: mayafbx.FbxImportOptions.bake_animation_layers
.. autoattribute:: mayafbx.FbxImportOptions.optical_markers
.. autoattribute:: mayafbx.FbxImportOptions.quaternion_interpolation
.. autoattribute:: mayafbx.FbxImportOptions.protect_driven_keys
.. autoattribute:: mayafbx.FbxImportOptions.deforming_elements_to_joint
.. autoattribute:: mayafbx.FbxImportOptions.deformation
.. autoattribute:: mayafbx.FbxImportOptions.deformation_skins
.. autoattribute:: mayafbx.FbxImportOptions.deformation_shapes
.. autoattribute:: mayafbx.FbxImportOptions.deformation_normalize_weights
.. autoattribute:: mayafbx.FbxImportOptions.sampling_rate
.. autoattribute:: mayafbx.FbxImportOptions.set_maya_framerate
.. autoattribute:: mayafbx.FbxImportOptions.keep_attributes_locked
.. autoattribute:: mayafbx.FbxImportOptions.custom_sampling_rate

|

Include
^^^^^^^

.. autoattribute:: mayafbx.FbxImportOptions.constraints
.. autoattribute:: mayafbx.FbxImportOptions.skeleton_definition
.. autoattribute:: mayafbx.FbxImportOptions.cameras
.. autoattribute:: mayafbx.FbxImportOptions.lights
.. autoattribute:: mayafbx.FbxImportOptions.audio

|

Advanced
^^^^^^^^

.. autoattribute:: mayafbx.FbxImportOptions.automatic_units
.. autoattribute:: mayafbx.FbxImportOptions.convert_units_to
.. autoattribute:: mayafbx.FbxImportOptions.axis_conversion
.. autoattribute:: mayafbx.FbxImportOptions.up_axis
.. autoattribute:: mayafbx.FbxImportOptions.forced_file_axis
.. autoattribute:: mayafbx.FbxImportOptions.show_warning_ui
.. autoattribute:: mayafbx.FbxImportOptions.generate_log

|

--------------------

Enums
======

.. autoclass:: mayafbx::QuaternionInterpolation
    :members:
    :undoc-members:

|

.. autoclass:: mayafbx::ConvertUnit
    :members:
    :undoc-members:

|

.. autoclass:: mayafbx::UpAxis
    :members:
    :undoc-members:

|

.. autoclass:: mayafbx::ForcedFileAxis
    :members:
    :undoc-members:

|

.. autoclass:: mayafbx::AxisConversionMethod
    :members:
    :undoc-members:

|

.. autoclass:: mayafbx::NurbsSurfaceAs
    :members:
    :undoc-members:

|

.. autoclass:: mayafbx::FileFormat
    :members:
    :undoc-members:

|

.. autoclass:: mayafbx::FileVersion
    :members:
    :undoc-members:

|

.. autoclass:: mayafbx::SkeletonDefinition
    :members:
    :undoc-members:

|

.. autoclass:: mayafbx::MergeMode
    :members:
    :undoc-members:

|

.. autoclass:: mayafbx::SamplingRate
    :members:
    :undoc-members:
