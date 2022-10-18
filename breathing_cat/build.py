"""Build the documentation based on sphinx and doxygen.

License BSD-3-Clause
Copyright (c) 2021, New York University and Max Planck Gesellschaft.
"""
import collections.abc
import fnmatch
import os
import shutil
import subprocess
import sys
import textwrap
import typing
from pathlib import Path

from . import config as _config


PathLike = typing.Union[str, os.PathLike]
FileFormat = typing.Literal["md", "rst", "txt"]


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


def _build_doxygen_xml(
    doc_build_dir: Path, project_source_dir: Path, doxygen_config: dict
) -> None:
    """
    Use doxygen to parse the C++ source files and generate a corresponding xml
    entry.

    Args:
        doc_build_dir: Path to where the doc should be built
        project_source_dir: Path to the source file of the project.
        doxygen_config: User-defined configuration for the Doxygen.
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

    # If multiple exclude patterns are provided, join them to a multi-line string
    # where each line has a \ at the end (this is how doxygen expects multiple
    # values).
    doxygen_exclude_patterns = " \\ \n".join(doxygen_config["exclude_patterns"])
    # replace ${PACKAGE_DIR} in the patterns
    doxygen_exclude_patterns = doxygen_exclude_patterns.replace(
        "${PACKAGE_DIR}", str(project_source_dir)
    )

    # Where to put the doxygen output.
    doxygen_output = doc_build_dir / "doxygen"

    # Parse the Doxyfile.in and replace the value between '@'
    with open(doxyfile_in, "rt") as f:
        doxyfile_out_text = (
            f.read()
            .replace("@PROJECT_NAME@", project_name)
            .replace("@PROJECT_SOURCE_DIR@", os.fspath(project_source_dir))
            .replace("@DOXYGEN_FILE_PATTERNS@", doxygen_file_patterns)
            .replace("@DOXYGEN_EXCLUDE_PATTERNS@", doxygen_exclude_patterns)
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


def _build_breath_api_doc(doc_build_dir: Path) -> None:
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


def _build_sphinx_api_doc(doc_build_dir: Path, python_source_dir: Path) -> None:
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


def _build_sphinx_build(doc_build_dir: Path) -> None:
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
    doc_build_dir: Path, project_source_dir: Path, resource_dir: Path, config: dict
) -> str:
    """Search if there is a C++ api do document, and document it.

    Args:
        doc_build_dir: Path where to create the temporary output.
        project_source_dir: Path to the source file of the project.
        resource_dir: Path to the resources files for the build.
        config: User configuration.

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
        _build_doxygen_xml(doc_build_dir, project_source_dir, config["doxygen"])
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


def _copy_readme(source_dir: Path, destination_dir: Path) -> FileFormat:
    """Searches for a README in the source and copies it to the destination directory .

    Searches for a "README.md" or "README.rst" (case-insensitive) in the source
    directory and copies it to the destination directory.  Returns the format of the
    file.

    Args:
        source_dir: Where to look for the README file.
        destination_dir: Directory to which the README is copied.

    Returns:
        Format of the README file.

    Raises
        FileNotFoundError: If no README is found in the source directory.
    """
    # map allowed readme file names to file format
    options: typing.Dict[str, FileFormat] = {
        "readme.md": "md",
        "readme.rst": "rst",
        "readme": "txt",
        "readme.txt": "txt",
    }

    readmes = [p.resolve() for p in source_dir.glob("*") if p.name.lower() in options]
    if not readmes:
        raise FileNotFoundError(f"No README file found in {source_dir}")

    # if multiple READMEs are found, print warning and use the first one that was found
    if len(readmes) > 1:
        print(f"WARNING: Found multiple README files in {source_dir}.", file=sys.stderr)

    readme = readmes[0]
    readme_format = options[readme.name.lower()]
    target_filename = f"readme.{readme_format}"
    shutil.copy(readme, destination_dir / target_filename)

    return readme_format


def _copy_license(source_dir: Path, destination_dir: Path) -> None:
    """Searches for a license in the source and copies it to the destination directory.

    Args:
        source_dir: Where to look for the README file.
        destination_dir: Directory to which the README is copied.

    Raises
        FileNotFoundError: If no README is found in the source directory.
    """
    license_file = [
        p.resolve()
        for p in source_dir.glob("*")
        if p.name in ["LICENSE", "license.txt"]
    ]
    if not license_file:
        raise FileNotFoundError(f"No license file found in {source_dir}")

    shutil.copy(license_file[0], destination_dir / "license.txt")


def _search_for_readme(project_source_dir: Path, doc_build_dir: Path) -> str:
    """Copy README file to build directory and return RST code to include it.

    Args:
        project_source_dir: Where to look for the file.
        doc_build_dir: Directory to which the is copied.

    Returns:
        RST snippet for including the README.  In case no README is found an empty
        string is return.
    """
    try:
        readme_format = _copy_readme(project_source_dir, doc_build_dir)
        # the include command differs depending on the format of the README
        if readme_format == "md":
            readme_include = textwrap.dedent(
                """
                .. include:: readme.md
                   :parser: myst_parser.sphinx_
            """
            )
        elif readme_format == "txt":
            readme_include = textwrap.dedent(
                """
                .. include:: readme.txt
                   :literal:
            """
            )
        else:
            readme_include = ".. include:: readme.rst"
    except FileNotFoundError:
        readme_include = ""

    return readme_include


def _search_for_license(project_source_dir: Path, doc_build_dir: Path) -> str:
    """Copy license file to build directory and return RST code to include it.

    Args:
        project_source_dir: Where to look for the file.
        doc_build_dir: Directory to which the is copied.

    Returns:
        RST snippet for including the license.  In case no license is found an empty
        string is return.
    """
    try:
        _copy_license(project_source_dir, doc_build_dir)
        license_include = textwrap.dedent(
            """
            License and Copyrights
            ----------------------

            .. include:: license.txt
        """
        )
    except FileNotFoundError:
        license_include = ""

    return license_include


def _construct_intersphinx_mapping_config(
    mapping_config: typing.Mapping[
        str,
        typing.Union[
            str,
            typing.Mapping[typing.Literal["target", "inventory"], typing.Optional[str]],
        ],
    ]
) -> str:
    """Construct argument for intersphinx_mapping parameter.

    The config can be given in a complete form, providing both target URL and inventory
    file name or a short version with only the target URL:

    .. code-block:: python

        {
            # short variant for convenience (if inventory=None)
            "pkg1": "https://docs.pkg1.com",
            # long variant for full support
            "pkg2": {
                "target": "https://pkg2.org/docs",
                "inventory": "my_inv.txt"
            },
        }

    Args:
        mapping_config: Dictionary with the mapping configuration.

    Returns:
        Python code that defines a dictionary that can be assigned to
        ``intersphinx_mapping``.
    """
    pattern = "'{name}': ({target!r}, {inventory!r})"
    mappings = []

    for name, params in mapping_config.items():
        if isinstance(params, str):
            params = {"target": params, "inventory": None}

        # make sure types are correct (so that using repr is save)
        assert isinstance(name, str)
        assert isinstance(params, collections.abc.Mapping)
        assert isinstance(params["target"], str)
        assert params["inventory"] is None or isinstance(params["inventory"], str)

        mappings.append(
            pattern.format(
                name=name, target=params["target"], inventory=params["inventory"]
            )
        )

    return "{" + ", ".join(mappings) + "}"


def build_documentation(
    build_dir: PathLike,
    project_source_dir: PathLike,
    project_version: str,
    python_pkg_path: typing.Optional[PathLike] = None,
    config_file: typing.Optional[PathLike] = None,
) -> None:
    # make sure all paths are of type Path
    doc_build_dir = Path(build_dir)
    project_source_dir = Path(project_source_dir)
    if python_pkg_path is not None:
        python_pkg_path = Path(python_pkg_path)

    # use default config in none is given
    if config_file is not None:
        config = _config.load_config(config_file)
    else:
        config = _config.find_and_load_config(project_source_dir)

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

    cpp_api = _search_for_cpp_api(
        doc_build_dir, project_source_dir, resource_dir, config
    )

    python_api = _search_for_python_api(
        doc_build_dir, project_source_dir, python_pkg_path
    )

    cmake_api = _search_for_cmake_api(doc_build_dir, project_source_dir, resource_dir)

    general_documentation = _search_for_general_documentation(
        doc_build_dir, project_source_dir, resource_dir
    )

    #
    # Copy the license and readme file.
    #
    readme_include = _search_for_readme(project_source_dir, doc_build_dir)
    license_include = _search_for_license(project_source_dir, doc_build_dir)

    #
    # Configure the conf.py and the index.rst.
    #

    # intersphinx config
    intersphinx_mapping = _construct_intersphinx_mapping_config(
        config["intersphinx"]["mapping"]
    )

    # configure the index.rst.in.
    header = "Welcome to " + project_name + "'s documentation!"
    header += "\n" + len(header) * "=" + "\n"
    with open(resource_dir / "sphinx" / "index.rst.in", "rt") as f:
        out_text = (
            f.read()
            .replace("@HEADER@", header)
            .replace("@README@", readme_include)
            .replace("@GENERAL_DOCUMENTATION@", general_documentation)
            .replace("@CPP_API@", cpp_api)
            .replace("@PYTHON_API@", python_api)
            .replace("@CMAKE_API@", cmake_api)
            .replace("@LICENSE@", license_include)
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
            .replace("@INTERSPHINX_MAPPING@", intersphinx_mapping)
        )
    with open(doc_build_dir / "conf.py", "wt") as f:
        f.write(out_text)

    # copy the custom.css to _static
    static_dir = doc_build_dir / "_static"
    static_dir.mkdir(exist_ok=True)
    shutil.copy(
        resource_dir / "sphinx" / "custom.css.in",
        static_dir / "custom.css",
    )

    #
    # Generate the html doc
    #
    _build_sphinx_build(doc_build_dir)
