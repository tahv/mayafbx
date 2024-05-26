# Changelog

## [unreleased]

- complete project rewrite.
- dropped support for Python `< 3.7`. Minimum supported Maya version is now `2022`.
- removed `FbxExportOptions.selected`, `export_fbx` takes a `selection` argument instead.
- `export_fbx` now has an optional `takes` argument to export a list of animation takes.
- many properties in `FbxExportOptions` and `FbxImportOptions`
  have been renamed to stick more closely to the names in Autodesk documentation.
  For example, `FbxExportOptions.selected_hierarchy` 
  was renamed to `FbxExportOptions.include_children`.
- added new properties in `FbxExportOptions`, including:
  `referenced_asset_content`, `pivot_to_nulls` or `bypass_rrs_inheritance`.
- all enums names have been uppercased. 
  For example: `QuaternionInterpolation.kResampleAsEuler` 
  was renamed `QuaternionInterpolation.RESAMPLE_AS_EULER`.

## 0.1.0 - 2021-02-14

- Initial release.
