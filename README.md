Documentation Builder for C++ and Python packages
=================================================

breathing_cat is a tool for building documentation that is used for some of the
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

Simply clone this repository and install it with

```
cd path/to/breathing-cat
pip install .
```

Note that for building C++ API documentation Doxygen is used, which needs to be
installed separately (e.g. with `sudo apt install doxygen` on Ubuntu).


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
```


Assumptions Regarding Package Structure
---------------------------------------

TODO


Copyright & License
-------------------

Copyright (c) 2022, New York University and Max Planck Gesellschaft.

License: BSD 3-clause (see LICENSE).
