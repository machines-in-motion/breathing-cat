# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Try to auto-detect package version if not explicitly specified.
- Install executable `mpiis-doc-build`.
- Short arguments `-p`/`-o` for `--package-dir`/`--output-dir`.

### Changed
- Renamed `--project-version` to `--package-version`.

### Fixed
- Workaround for an incompatibility issue between the RTD theme and autodoc, which
  caused class properties to be floating (see
  https://github.com/readthedocs/sphinx_rtd_theme/issues/1247)

## [0.1.0] - 2022-09-08
Extracted the documentation build code from
[mpi_cmake_modules](https://github.com/machines-in-motion/mpi_cmake_modules) with only
some minor changes. 
