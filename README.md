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
# The string '{{PACKAGE_DIR}}' in the patterns is replaced with the path to the package.
# It is recommended to put this at the beginning of patterns to avoid unintended matches
# on higher up parts on the path, which would result in *all* the files of the package
# being excluded.
# Example:
# exclude_patterns = ["{{PACKAGE_DIR}}/include/some_third_party_lib/*"]
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


[html]
# Path to an image that is shown at the top of the navigation bar.
# The image should be located inside the "doc/" folder and the path given relative to
# the package root.
# Example:
# logo = "doc/images/logo.png"
logo = ""


[mainpage]
# Custom title for the main page.  If not set "Welcome to {package}'s documentation!" is
# used.
# Example:
# title = "Custom Mainpage Title"
title = ""

# Automatically add files from the doc/ folder to a toctree, thus including them in the
# documentation.  Set this to false if you want to manually provide a toctree in the
# doc_mainpage or README file.
auto_general_docs = true
```


Include Files From Source Directory in the Documentation
--------------------------------------------------------

You may want to include files from the package into the documentation text.  For example
the package may contain a file `scripts/example.py` which could normally be included in
a file `doc/examples.rst` like this:

```rst
.. literalinclude:: ../scripts/example.py
```

With breathing cat, this unfortunately doesn't work, as all the documentation files are
copied to a separate build directory and processed there.  From within this build
directory, the relative path given above cannot be resolved.  However, a symlink called
"PKG" is created in the build directory and points to the package source directory.  So
instead of the above, you can use the following (note the leading `/`):

```rst
.. literalinclude:: /PKG/scripts/example.py
```


Assumptions Regarding Package Structure
---------------------------------------

Breathing Cat makes the following assumptions regarding the structure of the documented
package:

- The directory containing the package has the same name as the actual package.
- If the package contains one of the following files (case insensitive) in the root
  directory, it is included into the documentations main page:
  ```
  doc_mainpage.rst, doc_mainpage.md, README.rst, README.md, README.txt, README
  ```
  If there are multiple matches, only the first one is used with precedence based on the
  list above.

  Since `doc_mainpage.{rst,md}` has highest precedence, it can be provided in addition
  to a README.  This is useful if you want to have different content in the README and
  on the documentation main page.
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
  alphabetical order.  This can be disabled via the config parameter
  `mainpage.auto_general_docs` (see above) in case you want to manually provide a
  toctree.



Special Directives/Roles
------------------------

### confval

The `confval` directive can be used to specify configuration values.  It will be
rendered similarly like a class member and can be linked to.  Further the `confval` role
can be used to reference it in other parts for the documentation.

Example:

```rst
.. confval:: enable_foo: bool = False

   Here is some description of the parameter.
   Note that the type annotation and default value are both optional.

...

To reference the option, use :confval:`enable_foo`.
```


Copyright & License
-------------------

Copyright (c) 2022, New York University and Max Planck Gesellschaft.

License: BSD 3-clause (see LICENSE).
