# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- If the package root contains a file `doc_mainpage.{rst,md}`, it is used instead of the
  README to fill the main page.  This is useful if the content of the README is not
  suitable for the documentation main page.

## [1.1.1] - 2022-11-11
### Fixed
- Fixed issue with configuration validation that rejected valid intersphinx mapping
  configuration.


## [1.1.0] - 2022-11-04
### Changed
- Syntax for the package directory variable in the doxygen.excluded_patterns
  config is now `{{PACKAGE_DIR}}`.  The old `${PACKAGE_DIR}` is still supported
  for now but deprecated (see below).

### Deprecated
- Using `${PACKAGE_DIR}` in the doxygen.excluded_patterns config is deprecated,
  use `{{PACKAGE_DIR}}` instead.


## [1.0.0] - 2022-10-21
### Added
- Support for plain text READMEs ("README" or "README.TXT").
- Try to auto-detect package version if not explicitly specified.
- Install executable `bcat`.
- Short arguments `-p`/`-o` for `--package-dir`/`--output-dir`.
- Provide additional configuration via `breathing_cat.toml`
- Add `DOXYGEN_EXCLUDE_PATTERNS` via config file.
- Add intersphinx mappings via config file.

### Changed
- If multiple READMEs are found, do not prefer a specific type but simply use the first
  one found.
- Renamed `--project-version` to `--package-version`.
- Use MyST parser instead of recommonmark and m2r for including Markdown files.

### Fixed
- Workaround for an incompatibility issue between the RTD theme and autodoc, which
  caused class properties to be floating (see
  https://github.com/readthedocs/sphinx_rtd_theme/issues/1247)


## [0.1.0] - 2022-09-08
Extracted the documentation build code from
[mpi_cmake_modules](https://github.com/machines-in-motion/mpi_cmake_modules) with only
some minor changes. 


[Unreleased]: https://github.com/machines-in-motion/breathing-cat/compare/v1.1.1...HEAD
[1.1.1]: https://github.com/machines-in-motion/breathing-cat/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/machines-in-motion/breathing-cat/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/machines-in-motion/breathing-cat/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/machines-in-motion/breathing-cat/releases/tag/v0.1.0
