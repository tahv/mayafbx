# Changelog

## [unreleased]

- Complete project rewrite.
- Dropped support for Python `< 3.7`. Minimum supported Maya version is now `2022`.
- Added `FbxExportOptions.referenced_asset_content`.
- Renamed `FbxExportOptions.bake_animation`
  to `FbxExportOptions.bake_complexe_animation`.
- Renamed `FbxExportOptions.curve_filter_constant_key_reducer`
  to `FbxExportOptions.constant_key_reducer`.
- Renamed `FbxExportOptions.curve_filter_precision_translation`
  to `FbxExportOptions.constant_key_reducer_translation_precision`.
- Renamed `FbxExportOptions.curve_filter_precision_rotation`
  to `FbxExportOptions.constant_key_reducer_rotation_precision`.
- Renamed `FbxExportOptions.curve_filter_precision_scale`
  to `FbxExportOptions.constant_key_reducer_scale_precision`.
- Renamed `FbxExportOptions.curve_filter_precision_other`
  to `FbxExportOptions.constant_key_reducer_other_precision`.
- Renamed `FbxExportOptions.curve_filter_auto_tangents_only`
  to `FbxExportOptions.constant_key_reducer_auto_tangents_only`.
- Added `FbxExportOptions.pivot_to_nulls`.
- Added `FbxExportOptions.bypass_rrs_inheritance`.
- Removed `FbxExportOptions.selected`,
  `selection` is now a parameter of the `export_fbx` function.
- Renamed `FbxExportOptions.selected_hierarchy`
  to `FbxExportOptions.include_children`.
- Renamed `FbxExportOptions.selected_input_connections`
  to `FbxExportOptions.input_connections`.


## 0.1.0 - 2021-02-14

- Initial release.
