# Changelog

## 1.0.0 - 2024-05-30

- Dropped support for Python `< 3.7`.
  Minimum supported Maya version is now `2022`.
- Removed `FbxExportOptions.selected`,
  `export_fbx` takes a `selection` argument instead.
- `export_fbx` now has an optional `takes` argument to export a list of
  animation takes.
- Properties of `FbxExportOptions`
  and `FbxImportOptions` have been renamed to match their names in Autodesk
  documentation, e.g., `FbxExportOptions.selected_hierarchy` was renamed to
  `FbxExportOptions.include_children`.
- Added new properties in `FbxExportOptions`: `referenced_asset_content`,
  `pivot_to_nulls`, `bypass_rrs_inheritance`.
- Enums names have been uppercased, e.g.,
  `QuaternionInterpolation.kResampleAsEuler` was renamed to
  `QuaternionInterpolation.RESAMPLE_AS_EULER`.

## 0.1.0 - 2021-02-14

- Initial release.
