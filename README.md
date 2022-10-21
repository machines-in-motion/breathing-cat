Documentation Builder for C++ and Python packages
=================================================

Breathing Cat is a tool for building documentation that is used for some of the
software packages developed at the Max Planck Institute for Intelligent Systems (MPI-IS)
and the New York University.

It is basically a wrapper around Doxygen, Sphinx and Breathe and runs those tools to
generate a Sphinx-based documentation, automatically including API documentation for
C++, Python and CMake code found in the package.

It is tailored to work with the structure of our packages but we are doing nothing
extraordinary there, so it will likely work for others as well (see below for the
assumptions we make regarding the package structure).


Installation
------------

Breathing Cat depends on [Doxygen](https://doxygen.nl) for generating C++ documentation.
As Doxygen cannot automatically be installed as dependency by pip, it needs to be
installed manually.  For example on Ubuntu:
```
sudo apt install doxygen
```

To install Breathing Cat with all further dependencies:
```
pip install breathing_cat
```


Usage
-----

In the most simple case you can run it like this:

```
bcat --package-dir path/to/package --output-dir path/to/output
```

If no package version is specified, `bcat` tries to find it by checking a
number of files in the package directory.  If no version is found this way, it fails
with an error.  In this case, you can explicitly specify the version using
`--package-version`.

`bcat` tries to automatically detect if the package contains Python code and,
if yes, adds a Python API section to the documentation.  However, if your package
contains Python modules that are only generated at build-time (e.g. Python bindings for
C++ code) you can use `--python-dir` to specify the directory where the Python modules
are installed to.  This way, the generated modules will be included in the documentation
as well.

For a complete list of options see `bcat --help`.

Instead of the `bcat` executable, you can also use `python -m breathing_cat`.


Configuration
-------------

A package can contain an optional config file `breathing_cat.toml` which has to be
placed either in the root directory of the package or in `doc[s]/`.

Below is an exemplary config file, including all available options with their default
values:

```toml
[doxygen]
# List of patterns added to DOXYGEN_EXCLUDE_PATTERNS (see doxygen documentation).
# The string '${PACKAGE_DIR}' in the patterns is replaced with the path to the package.
# It is recommended to put this at the beginning of patterns to avoid unintended matches
# on higher up parts on the path, which would result in *all* the files of the package
# being excluded.
# Example:
# exclude_patterns = ["${PACKAGE_DIR}/include/some_third_party_lib/*"]
exclude_patterns = []


[intersphinx.mapping]
# Add intersphinx mappings.  See intersphinx documentation for the meaning of the
# values.
# Two notations are supported:
#
# 1. Long notation (results in `'foo': ('docs.foo.org', 'my_inv.txt'):
# foo = {target = "docs.foo.org", inventory = "my_inv.txt"}
#
# 2. # Short notation (results in `'foo': ('docs.foo.org', None):
# foo = "docs.foo.org"
```


Assumptions Regarding Package Structure
---------------------------------------

Breathing Cat makes the following assumptions regarding the structure of the documented
package:

- The directory containing the package has the same name as the actual package.
- The package may contain a README file that has one of the following names (case
  insensitive):  `README`, `README.txt`, `README.md`, `README.rst`
- The package may contain a license file called `LICENSE` or `license.txt`.
- C++ code is documented using Doxygen comments in the header files.
- C++ header files are located outside of `src/` (typically in `include/`).
- Python code is documented using docstrings (supported formats are standard Sphinx,
  NumPy Style and Google Style).
- The Python code is located in one of the following directories (relative to the
  package root):

  - `<package_name>/`
  - `python/<package_name>/`
  - `src/<package_name>/`

- CMake files that should be documented are located in `cmake/` and use the directives
  provided by the
  [sphinxcontrib.moderncmakedomain](https://github.com/scikit-build/moderncmakedomain)
  extension.
- General documentation is provided in reStructuredText- or Markdown-files located in
  `doc/` or `docs/`.  All files found in this directory are automatically included in
  alphabetical order.


Copyright & License
-------------------

Copyright (c) 2022, New York University and Max Planck Gesellschaft.

License: BSD 3-clause (see LICENSE).
