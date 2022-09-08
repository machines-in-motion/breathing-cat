"""Build the documentation based on sphinx and doxygen.

License BSD-3-Clause
Copyright (c) 2021, New York University and Max Planck Gesellschaft.
"""

import fnmatch
import os
import shutil
import subprocess
import textwrap
import typing
from pathlib import Path


PathLike = typing.Union[str, os.PathLike]


def _get_cpp_file_patterns() -> typing.List[str]:
    return ["*.h", "*.hh", "*.hpp", "*.hxx", "*.cpp", "*.c", "*.cc"]


def _find_doxygen() -> str:
    """Find the full path to the doxygen executable.

    Raises:
        Exception: if the doxygen executable is not found.

    Returns:
        The full path to the doxygen executable.
    """
    exec_path = shutil.which("doxygen")
    if exec_path is not None:
        return exec_path
    raise Exception(
        "doxygen executable not found. You may try " "'(sudo ) apt install doxygen*'"
    )


def _find_breathe_apidoc() -> str:
    """Find the full path to the breathe-apidoc executable.

    Raises:
        Exception: if the breathe-apidoc executable is not found.

    Returns:
        The full path to the black executable.
    """
    exec_path = shutil.which("breathe-apidoc")
    if exec_path is not None:
        return exec_path
    raise Exception(
        "breathe-apidoc executable not found. You may try "
        "'(sudo -H) pip3 install breathe'"
    )


def _find_sphinx_apidoc() -> str:
    """Find the full path to the sphinx-apidoc executable.

    Raises:
        Exception: if the sphinx-apidoc executable is not found.

    Returns:
        The full path to the black executable.
    """
    exec_path = shutil.which("sphinx-apidoc")
    if exec_path is not None:
        return exec_path
    raise Exception(
        "sphinx-apidoc executable not found. You may try "
        "'(sudo -H) pip3 install sphinx'"
    )


def _find_sphinx_build() -> str:
    """Find the full path to the sphinx-build executable.

    Raises:
        Exception: if the sphinx-build executable is not found.

    Returns:
        The full path to the black executable.
    """
    exec_path = shutil.which("sphinx-build")
    if exec_path is not None:
        return exec_path

    raise Exception(
        "sphinx-build executable not found. You may try "
        "'(sudo -H) pip3 install sphinx'"
    )


def _resource_path() -> Path:
    """
    Fetch the resources path. It contains all the configuration files
    for the different executables: Doxyfile, conf.py, etc.

    Raises:
        AssertionError: if the resources folder is not found.

    Returns:
        pathlib.Path: Path to the configuration files.
    """
    this_dir = Path(__file__).parent
    resource_path = this_dir / "resources"

    assert resource_path.is_dir()

    return resource_path


def _build_doxygen_xml(doc_build_dir: Path, project_source_dir: Path):
    """
    Use doxygen to parse the C++ source files and generate a corresponding xml
    entry.

    Args:
        doc_build_dir (str): Path to where the doc should be built
        project_source_dir (str): Path to the source file of the project.
    """
    # Get project_name
    project_name = project_source_dir.name

    # Get the doxygen executable.
    doxygen = _find_doxygen()

    # Get the resources path.
    resource_path = _resource_path()

    # get the Doxyfile.in file
    doxyfile_in = resource_path / "doxygen" / "Doxyfile.in"
    assert doxyfile_in.is_file()

    # Which files are going to be parsed.
    doxygen_file_patterns = " ".join(_get_cpp_file_patterns())

    # Where to put the doxygen output.
    doxygen_output = doc_build_dir / "doxygen"

    # Parse the Doxyfile.in and replace the value between '@'
    with open(doxyfile_in, "rt") as f:
        doxyfile_out_text = (
            f.read()
            .replace("@PROJECT_NAME@", project_name)
            .replace("@PROJECT_SOURCE_DIR@", os.fspath(project_source_dir))
            .replace("@DOXYGEN_FILE_PATTERNS@", doxygen_file_patterns)
            .replace("@DOXYGEN_OUTPUT@", str(doxygen_output))
        )
    doxyfile_out = doxygen_output / "Doxyfile"
    doxyfile_out.parent.mkdir(parents=True, exist_ok=True)
    with open(doxyfile_out, "wt") as f:
        f.write(doxyfile_out_text)

    bashCommand = doxygen + " " + str(doxyfile_out)
    process = subprocess.Popen(
        bashCommand.split(), stdout=subprocess.PIPE, cwd=str(doxygen_output)
    )
    output, error = process.communicate()
    print("Doxygen output:\n", output.decode("UTF-8"))
    print("Doxygen error:\n", error)
    print("")


def _build_breath_api_doc(doc_build_dir: Path):
    """
    Use breathe_apidoc to parse the xml output from Doxygen and generate
    '.rst' files.

    Args:
        doc_build_dir (str): Path where to create the temporary output.
    """
    breathe_apidoc = _find_breathe_apidoc()
    breathe_input = doc_build_dir / "doxygen" / "xml"
    breathe_output = doc_build_dir / "breathe_apidoc"
    breathe_option = "-f -g class,interface,struct,union,file,namespace,group"

    bashCommand = (
        breathe_apidoc
        + " -o "
        + str(breathe_output)
        + " "
        + str(breathe_input)
        + " "
        + str(breathe_option)
    )
    process = subprocess.Popen(
        bashCommand.split(), stdout=subprocess.PIPE, cwd=str(doc_build_dir)
    )
    output, error = process.communicate()
    print("breathe-apidoc output:\n", output.decode("UTF-8"))
    print("breathe-apidoc error:\n", error)
    print("")


def _build_sphinx_api_doc(doc_build_dir: Path, python_source_dir: Path):
    """
    Use sphinx_apidoc to parse the python files output from Doxygen and
    generate '.rst' files.

    Args:
        doc_build_dir (str): Path where to create the temporary output.
        project_source_dir (str): Path to the source file of the project.
    """
    # define input folder
    if python_source_dir.is_dir():
        sphinx_apidoc = _find_sphinx_apidoc()
        sphinx_apidoc_input = str(python_source_dir)
        sphinx_apidoc_output = str(doc_build_dir)

        bashCommand = (
            sphinx_apidoc
            + " --separate "
            + " -o "
            + sphinx_apidoc_output
            + " "
            + sphinx_apidoc_input
        )
        process = subprocess.Popen(
            bashCommand.split(), stdout=subprocess.PIPE, cwd=str(doc_build_dir)
        )
        output, error = process.communicate()
        print("sphinx-apidoc output:\n", output.decode("UTF-8"))
        print("sphinx-apidoc error:\n", error)

    else:
        print("No python module for sphinx-apidoc to parse.")
    print("")


def _build_sphinx_build(doc_build_dir: Path):
    """
    Use sphinx_build to parse the cmake and rst files previously generated and
    generate the final html layout.

    Args:
        doc_build_dir (str): Path where to create the temporary output.
    """
    sphinx_build = _find_sphinx_build()
    bashCommand = (
        sphinx_build + " -M html " + str(doc_build_dir) + " " + str(doc_build_dir)
    )
    process = subprocess.Popen(
        bashCommand.split(), stdout=subprocess.PIPE, cwd=str(doc_build_dir)
    )
    output, error = process.communicate()
    print("sphinx-apidoc output:\n", output.decode("UTF-8"))
    print("sphinx-apidoc error:\n", error)


def _search_for_cpp_api(
    doc_build_dir: Path, project_source_dir: Path, resource_dir: Path
) -> str:
    """Search if there is a C++ api do document, and document it.

    Args:
        doc_build_dir (str): Path where to create the temporary output.
        project_source_dir (str): Path to the source file of the project.
        resource_dir (str): Path to the resources files for the build.

    Returns:
        str: String added to the main index.rst in case there is a C++ api.
    """
    cpp_api = ""

    # Search for C++ files
    has_cpp = False
    for p in project_source_dir.glob("**/*"):
        if any(
            fnmatch.fnmatch(str(p), pattern) for pattern in _get_cpp_file_patterns()
        ):
            has_cpp = True
            break

    if has_cpp:
        print("Found C++ files, add C++ API documentation")

        # Introduce this toc tree in the main index.rst
        cpp_api = textwrap.dedent(
            """
            .. toctree::
               :caption: C++ API
               :maxdepth: 2

               doxygen_index

        """
        )
        # Copy the index of the C++ API.
        shutil.copy(
            resource_dir / "sphinx" / "doxygen_index_one_page.rst.in",
            doc_build_dir / "doxygen_index_one_page.rst",
        )
        shutil.copy(
            resource_dir / "sphinx" / "doxygen_index.rst.in",
            doc_build_dir / "doxygen_index.rst",
        )

        # Build the doxygen xml files.
        _build_doxygen_xml(doc_build_dir, project_source_dir)
        # Generate the .rst corresponding to the doxygen xml
        _build_breath_api_doc(doc_build_dir)

    else:
        print("No C++ files found.")

    return cpp_api


def _search_for_python_api(
    doc_build_dir: Path,
    project_source_dir: Path,
    package_path: typing.Optional[Path] = None,
) -> str:
    """Search for a Python API and build it's documentation.

    Args:
        doc_build_dir (str): Path where to create the temporary output.
        project_source_dir (str): Path to the source file of the project.

    Returns:
        str: String added to the main index.rst in case there is a Python api.
    """
    python_api = ""

    # Get the project name form the source path.
    project_name = project_source_dir.name

    if package_path is None:
        package_path_candidates = [
            project_source_dir / project_name,
            project_source_dir / "python" / project_name,
            project_source_dir / "src" / project_name,
        ]
        for p in package_path_candidates:
            if p.is_dir():
                package_path = p
                break

    # Search for Python API.
    if package_path:
        # Introduce this toc tree in the main index.rst
        python_api = textwrap.dedent(
            """
            .. toctree::
               :caption: Python API
               :maxdepth: 3

               modules

            * :ref:`modindex`

        """
        )
        _build_sphinx_api_doc(doc_build_dir, package_path)
    return python_api


def _search_for_cmake_api(
    doc_build_dir: Path, project_source_dir: Path, resource_dir: Path
) -> str:
    cmake_api = ""

    # Search for CMake API.
    cmake_files = [
        p.resolve()
        for p in project_source_dir.glob("cmake/*")
        if p.suffix in [".cmake"] or p.name == "CMakeLists.txt"
    ]
    if cmake_files:
        # Introduce this toc tree in the main index.rst
        cmake_api = textwrap.dedent(
            """
            .. toctree::
               :caption: CMake API
               :maxdepth: 3

               cmake_doc

        """
        )
        doc_cmake_module = ""
        for cmake_file in cmake_files:
            doc_cmake_module += cmake_file.stem + "\n"
            doc_cmake_module += len(cmake_file.stem) * "-" + "\n\n"
            doc_cmake_module += ".. cmake-module:: cmake/" + cmake_file.name + "\n\n"
        with open(resource_dir / "sphinx" / "cmake_doc.rst.in", "rt") as f:
            out_text = f.read().replace("@DOC_CMAKE_MODULE@", doc_cmake_module)
        with open(str(doc_build_dir / "cmake_doc.rst"), "wt") as f:
            f.write(out_text)

        shutil.copytree(
            project_source_dir / "cmake",
            doc_build_dir / "cmake",
        )

    return cmake_api


def _search_for_general_documentation(
    doc_build_dir: Path, project_source_dir: Path, resource_dir: Path
) -> str:
    general_documentation = ""

    doc_path_candidates = [
        project_source_dir / "doc",
        project_source_dir / "docs",
    ]
    doc_path = None
    for p in doc_path_candidates:
        if p.is_dir():
            doc_path = p
            break

    # Search for additional doc.
    if doc_path:
        general_documentation = textwrap.dedent(
            """
            .. toctree::
               :caption: General Documentation
               :maxdepth: 2

               general_documentation

        """
        )
        shutil.copy(
            resource_dir / "sphinx" / "general_documentation.rst.in",
            doc_build_dir / "general_documentation.rst",
        )
        shutil.copytree(
            doc_path,
            doc_build_dir / "doc",
        )
    return general_documentation


def build_documentation(
    build_dir: PathLike,
    project_source_dir: PathLike,
    project_version,
    python_pkg_path: typing.Optional[PathLike] = None,
):
    # make sure all paths are of type Path
    doc_build_dir = Path(build_dir)
    project_source_dir = Path(project_source_dir)
    if python_pkg_path is not None:
        python_pkg_path = Path(python_pkg_path)

    #
    # Initialize the paths
    #

    # Get the project name form the source path.
    project_name = project_source_dir.name

    # Create the folder architecture inside the build folder.
    shutil.rmtree(doc_build_dir, ignore_errors=True)
    doc_build_dir.mkdir(parents=True, exist_ok=True)

    # Get the path to resource files.
    resource_dir = Path(_resource_path())

    #
    # Parametrize the final doc layout depending we have CMake/Python/C++ api.
    #

    # String to replace in the main index.rst

    cpp_api = _search_for_cpp_api(doc_build_dir, project_source_dir, resource_dir)

    python_api = _search_for_python_api(
        doc_build_dir, project_source_dir, python_pkg_path
    )

    cmake_api = _search_for_cmake_api(doc_build_dir, project_source_dir, resource_dir)

    general_documentation = _search_for_general_documentation(
        doc_build_dir, project_source_dir, resource_dir
    )

    #
    # Configure the config.py and the index.rst.
    #

    # configure the index.rst.in.
    header = "Welcome to " + project_name + "'s documentation!"
    header += "\n" + len(header) * "=" + "\n"
    with open(resource_dir / "sphinx" / "index.rst.in", "rt") as f:
        out_text = (
            f.read()
            .replace("@HEADER@", header)
            .replace("@GENERAL_DOCUMENTATION@", general_documentation)
            .replace("@CPP_API@", cpp_api)
            .replace("@PYTHON_API@", python_api)
            .replace("@CMAKE_API@", cmake_api)
        )
    with open(doc_build_dir / "index.rst", "wt") as f:
        f.write(out_text)

    # configure the config.py.in.
    with open(resource_dir / "sphinx" / "conf.py.in", "rt") as f:
        out_text = (
            f.read()
            .replace("@PROJECT_SOURCE_DIR@", os.fspath(project_source_dir))
            .replace("@PROJECT_NAME@", project_name)
            .replace("@PROJECT_VERSION@", project_version)
            .replace("@DOXYGEN_XML_OUTPUT@", str(doc_build_dir / "doxygen" / "xml"))
        )
    with open(doc_build_dir / "conf.py", "wt") as f:
        f.write(out_text)

    #
    # Copy the license and readme file.
    #
    readme = [
        p.resolve()
        for p in project_source_dir.glob("*")
        if p.name.lower() in ["readme.md", "readme.rst"]
    ]
    # sort alphabetically so that "readme.md" is preferred in case both are
    # found
    readme = sorted(readme)
    if readme:
        shutil.copy(readme[0], doc_build_dir / "readme.md")

    license_file = [
        p.resolve()
        for p in project_source_dir.glob("*")
        if p.name in ["LICENSE", "license.txt"]
    ]
    if license_file:
        shutil.copy(license_file[0], doc_build_dir / "license.txt")

    #
    # Generate the html doc
    #
    _build_sphinx_build(doc_build_dir)
