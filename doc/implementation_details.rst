Implementation Details
======================

Introduction
------------

This page describes pipeline of tools used to build the documentation of a
package.

breathing-cat automatically integrates documentation from C++, Python, CMake,
Markdown and reStructuredText files. In order to process this we use a couple of
off-the-shelf softwares:

- `Sphinx <http://www.sphinx-doc.org/en/master/>`_: The main tool for building
  the overall documentation and creating the
  Python API documentation from docstrings.
- `Doxygen <http://www.doxygen.nl/>`_: For parsing in-source C++ API
  documentation.
- `Breathe <https://breathe.readthedocs.io/en/latest/>`_: A sphinx extension
  that generates reStructuredText files based on Doxygen's xml output.
- sphinxcontrib-moderncmakedomain: For generating CMake API documentation based
  on in-source comments.
- MyST parser: Add support for Markdown files as alternative to
  reStructuredText.


Advanced explanation on the tools
---------------------------------

Doxygen
~~~~~~~

In order to execute to generate the C++ API documentation we use Doxygen.
Breathing cat generates a ``Doxyfile`` based on the template in
``breathing_cat/resources/doxygen/Doxyfile.in``.

The file is set up to notably:

- Output the files in the ``_build/docs/doxygen`` folder with the
  ``OUTPUT_DIRECTORY`` parameter.
- Set ``GENERATE_HTML = No`` and ``GENERATE_XML = YES`` to generate a list of
  xml files containing the API documentation.


Breathe
~~~~~~~

Breathe is a sphinx extension that parses the Doxygen XML output.
It provides two import things:

- Directives that allow you to include object from the Doxygen XML output in the
  documentation.
- An executable ``breathe-apidoc`` that generates automatically the C++ API into
  reStructuredText files (similar to ``sphinx-apidoc`` for Python API).

In order to use it we need to add a couple of line in the ``conf.py`` used by
Sphinx:

.. code-block:: python

   extensions = [
       # ... other stuff
       'breathe', # to define the C++ api
       # ... other stuff
   ]

We also need to add the following variables that determine the behaviour of
Breathe:

.. code-block:: python

   # breath project names and paths. Here project is the name of the repos and
   # the path is the path to the Doxygen output.
   breathe_projects = { project: "../doxygen/xml" }
   # Default project used for all Doxygen output (we use only one here).
   breathe_default_project = project
   # By default we ask all informations to be displayed.
   breathe_default_members = ('members', 'private-members', 'undoc-members')

Once the ``conf.py`` is setup we execute ``breath-apidoc`` on the
Doxygen XML output:

::

   breathe-apidoc -o $(BREATHE_OUT) $(BREATHE_IN) $(BREATHE_OPTION)

with:

-  ``BREATHE_OUT`` the output path (``_build/docs/sphinx/breathe/``),
-  ``BREATHE_IN`` the path to the Doxygen xml output
   (``_build/docs/doxygen/xml/``),
-  and ``BREATHE_OPTION`` some output formatting option, here empty.

This generates a list of all classes, namespace and files in different
reStructuredText (``.rst``) files, which are included in the documentation.


MyST parser
~~~~~~~~~~~

By default Sphinx only supports reStructuredText.  Adding the `MyST parser
<https://myst-parser.readthedocs.io/en/latest/>`_ as extension adds additional
support for Markdown files.  Further, MyST extends standard Markdown with some
special syntax that allows to use rst directives and roles in Markdown files
(see the documentation of MyST for details).


We add it to the ``extensions`` variable in ``conf.py``:

.. code:: python

   extensions = [
       # ... other stuff
       'myst_parser', # markdown support
       # ... other stuff
   ]

Then we tell Sphinx to read the .md extension files in the ``conf.py``:

.. code:: python

   # The suffix(es) of source filenames.
   source_suffix = ['.rst', '.md']



sphinx-apidoc
~~~~~~~~~~~~~

``sphinx-apidoc`` is shipped with Sphinx and allows the generation of a Python
module API documentation extracting the doc string from the code. We need to add
to the PYTHONPATH the path to the Python module in the ``conf.py``:

.. code:: python

   sys.path.insert(0, os.path.abspath("path/to/the/python/module"))


And then build the API documentation by:

::

   sphinx_apidoc -o $(SPHINX_BUILD_OUT) path/to/the/python/module

Where ``SPHINX_BUILD_OUT`` is the output path.


sphinx-build
~~~~~~~~~~~~

``sphinx-build`` is the command to build the final documentation from the bits
generated in the steps above.
The tricky thing with ``sphinx-build`` is that everything included needs to be
in the working directory. Therefore in the build directory we set the output of
``breathe-apidoc`` and ``shpinx-apidoc`` to ``_build/docs/sphinx``. And inside
the same folder we create a symlink that points to the source ``doc/`` folder.

Therefore in order:

-  The ``index.rst`` includes the C++ API main ``.rst`` files from
   Breathe.
-  Then it includes the ``modules.rst`` file from ``sphinx-apidoc``
-  And then is adds all files inside ``doc/``, which, again, points
   toward the source ``doc/`` directory.

The command to execute is the following:

::

   sphinx-build -M html _build/docs/sphinx _build/docs/sphinx

This will generate the documentation website in ``_build/docs/sphinx/html/``
Therefore ``firefox _build/docs/sphinx/html/index.html`` opens the documentation
