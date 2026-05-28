# Changelog

## Unreleased

- [`f5e5804`](https://gitlab.com/tahv/mayafbx/-/commit/f5e5804) **docs:**
  switch to zensical ([!2](https://gitlab.com/tahv/mayafbx/-/merge_requests/1))
- [`f5e5804`](https://gitlab.com/tahv/mayafbx/-/commit/f5e5804) **docs:**
  various docstrings updates to conform to zensical parser
  ([!2](https://gitlab.com/tahv/mayafbx/-/merge_requests/1))
- [`9d673c8`](https://gitlab.com/tahv/mayafbx/-/commit/9d673c8)
  **BREAKING refactor!:** remove `FbxOptions`, `FbxProperty`,
  `FbxPropertyField`, `applied_options`, `apply_options`, `_T`, from public API
- [`470ef6a`](https://gitlab.com/tahv/mayafbx/-/commit/470ef6a) **feat:**
  expose `mayafbx.Take`
- [`b96379b`](https://gitlab.com/tahv/mayafbx/-/commit/b96379b)
  **BREAKING refactor!:** fixed typo in property name `bake_complex_animation`
- [`32fe46c`](https://gitlab.com/tahv/mayafbx/-/commit/32fe46c) **test:**
  get/set `FbxOption`
- [`b7a51fc`](https://gitlab.com/tahv/mayafbx/-/commit/b7a51fc) **style:**
  narrow `export_fbx` type hint
- [`25fff6a`](https://gitlab.com/tahv/mayafbx/-/commit/25fff6a) **fix:**
  fallback to `FbxPropertyField` default only when value is `None`

## [1.0.0](https://gitlab.com/tahv/mayafbx/-/releases/1.1.0) - 2024-05-30

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

## [0.1.0](https://gitlab.com/tahv/mayafbx/-/releases/0.1.0) - 2021-02-14

- Initial release.
