import typing
from pathlib import Path

import pytest

from breathing_cat.config import config_from_dict
from breathing_cat import build


@pytest.fixture()
def ros_pkg_path() -> Path:
    return Path(__file__).parent / "test_packages" / "ros_pkg"


@pytest.fixture()
def test_configs():
    return Path(__file__).parent / "config"


def test_resource_path() -> None:
    path = build._resource_path()
    # validate the path by checking for existence of a few files that should be there
    assert (path / "doxygen" / "Doxyfile.in").is_file()
    assert (path / "sphinx" / "conf.py.in").is_file()


def test_prepare_doxygen_exclude_patterns() -> None:
    pkg_path = Path("/tmp/foo")

    # old style variable (deprecated but currently still supported)
    config = config_from_dict({"doxygen": {"exclude_patterns": ["third_party*"]}})
    assert (
        build._prepare_doxygen_exclude_patterns(pkg_path, config["doxygen"])
        == "third_party*"
    )

    # using PACKAGE_DIR variable
    config = config_from_dict(
        {"doxygen": {"exclude_patterns": ["{{PACKAGE_DIR}}/third_party*"]}}
    )
    assert (
        build._prepare_doxygen_exclude_patterns(pkg_path, config["doxygen"])
        == "/tmp/foo/third_party*"
    )

    # using old variable style (deprecated but still supported)
    config = config_from_dict(
        {"doxygen": {"exclude_patterns": ["${PACKAGE_DIR}/third_party*"]}}
    )
    assert (
        build._prepare_doxygen_exclude_patterns(pkg_path, config["doxygen"])
        == "/tmp/foo/third_party*"
    )

    # multiple
    config = config_from_dict(
        {
            "doxygen": {
                "exclude_patterns": [
                    "something",
                    "{{PACKAGE_DIR}}/foobar",
                    "{{PACKAGE_DIR}}/third_party*",
                ]
            }
        }
    )
    assert (
        build._prepare_doxygen_exclude_patterns(pkg_path, config["doxygen"])
        == r"""something \
/tmp/foo/foobar \
/tmp/foo/third_party*"""
    )


def test_find_doxygen() -> None:
    path = build._find_doxygen()
    assert path.endswith("doxygen")

    with pytest.raises(build.ExecutableNotFoundError):
        build._find_doxygen(path="")


def test_find_breathe_apidoc() -> None:
    path = build._find_breathe_apidoc()
    assert path.endswith("breathe-apidoc")

    with pytest.raises(build.ExecutableNotFoundError):
        build._find_breathe_apidoc(path="")


def test_find_sphinx_apidoc() -> None:
    path = build._find_sphinx_apidoc()
    assert path.endswith("sphinx-apidoc")

    with pytest.raises(build.ExecutableNotFoundError):
        build._find_sphinx_apidoc(path="")


def test_find_sphinx_build() -> None:
    path = build._find_sphinx_build()
    assert path.endswith("sphinx-build")

    with pytest.raises(build.ExecutableNotFoundError):
        build._find_sphinx_build(path="")


def test_build_doxygen_xml(ros_pkg_path: Path, tmp_path: Path) -> None:
    build_dir = tmp_path

    config = {"exclude_patterns": ["{{PACKAGE_DIR}}/include/ros_pkg/third_party*"]}
    build._build_doxygen_xml(build_dir, ros_pkg_path, config)

    # verify creation of some files
    doxyfile = build_dir / "doxygen/Doxyfile"
    assert doxyfile.is_file()
    assert (build_dir / "doxygen/xml/class_foo.xml").is_file()

    # third_party.hpp was explicitly excluded, so should not show up in the generated
    # files
    assert not (build_dir / "doxygen/xml/class_third_party.xml").exists()

    # verify all @VARIABLES@ in Doxyfile have been substituted
    doxyfile_content = doxyfile.read_text()
    assert "@" not in doxyfile_content


def test_build_breathe_api_doc(ros_pkg_path: Path, tmp_path: Path) -> None:
    build_dir = tmp_path

    # need to run doxygen first
    config: typing.Dict[str, typing.Any] = {"exclude_patterns": []}
    build._build_doxygen_xml(build_dir, ros_pkg_path, config)
    build._build_breath_api_doc(build_dir)

    # verify for a few of the expected files that they were created
    breathe_dir = build_dir / "breathe_apidoc"
    assert (breathe_dir / "classlist.rst").is_file()
    assert (breathe_dir / "class/class_foo.rst").is_file()


def test_build_sphinx_api_doc(ros_pkg_path: Path, tmp_path: Path) -> None:
    build_dir = tmp_path
    build._build_sphinx_api_doc(build_dir, ros_pkg_path / "python/ros_pkg")

    # verify for a few of the expected files that they were created
    assert (build_dir / "modules.rst").is_file()
    assert (build_dir / "ros_pkg.foo.rst").is_file()


def test_search_for_cmake_api(ros_pkg_path: Path, tmp_path: Path) -> None:
    build_dir = tmp_path

    resource_dir = build._resource_path()
    build._search_for_cmake_api(build_dir, ros_pkg_path, resource_dir)

    cmake_doc_file = build_dir / "cmake_doc.rst"
    assert cmake_doc_file.is_file()
    assert (build_dir / "cmake/foo.cmake").is_file()

    # verify all @VARIABLES@ have been substituted
    cmake_doc_content = cmake_doc_file.read_text()
    assert "@" not in cmake_doc_content


def test_copy_general_documentation(ros_pkg_path: Path, tmp_path: Path) -> None:
    build_dir = tmp_path

    build._copy_general_documentation(ros_pkg_path, build_dir)

    assert (build_dir / "doc/getting_started.rst").is_file()
    assert (build_dir / "doc/contribute.md").is_file()


def test_create_general_documentation_toctree(tmp_path: Path) -> None:
    build_dir = tmp_path

    resource_dir = build._resource_path()
    build._create_general_documentation_toctree(build_dir, resource_dir)

    general_doc_file = build_dir / "general_documentation.rst"
    assert general_doc_file.is_file()

    # verify all @VARIABLES@ have been substituted
    general_doc_content = general_doc_file.read_text()
    assert "@" not in general_doc_content


def _test_copy_mainpage(tmp_path: Path, filename_in: str, filename_out: str) -> None:
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    pkg_dir = tmp_path / "pkg"
    pkg_dir.mkdir()
    readme = pkg_dir / filename_in
    readme.write_text("Hello")

    build._copy_mainpage(pkg_dir, build_dir)
    build_dir_content = [str(f.name) for f in build_dir.iterdir()]
    assert (
        build_dir / filename_out
    ).is_file(), f"{filename_out} not found.  build dir content: {build_dir_content}"
    assert (build_dir / filename_out).read_text() == "Hello"


def test_copy_mainpage_readme(tmp_path: Path) -> None:
    _test_copy_mainpage(tmp_path, "README", "mainpage.txt")


def test_copy_mainpage_readme_txt(tmp_path: Path) -> None:
    _test_copy_mainpage(tmp_path, "README.TXT", "mainpage.txt")


def test_copy_mainpage_readme_md(tmp_path: Path) -> None:
    _test_copy_mainpage(tmp_path, "README.md", "mainpage.md")


def test_copy_mainpage_readme_rst(tmp_path: Path) -> None:
    _test_copy_mainpage(tmp_path, "README.rst", "mainpage.rst")


def test_copy_mainpage_doc_mainpage_rst(tmp_path: Path) -> None:
    _test_copy_mainpage(tmp_path, "doc_mainpage.rst", "mainpage.rst")


def test_copy_mainpage_doc_mainpage_md(tmp_path: Path) -> None:
    _test_copy_mainpage(tmp_path, "doc_mainpage.md", "mainpage.md")


def test_copy_mainpage_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        _test_copy_mainpage(tmp_path, "wrong_name", "mainpage.rst")


def test_copy_mainpage_precedence(tmp_path: Path) -> None:
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    pkg_dir = tmp_path / "pkg"
    pkg_dir.mkdir()

    readme = pkg_dir / "README.rst"
    readme.write_text("This is the README")
    mainpage_rst = pkg_dir / "doc_mainpage.rst"
    mainpage_rst.write_text("This is the doc_mainpage.rst")

    build._copy_mainpage(pkg_dir, build_dir)
    build_dir_content = [str(f.name) for f in build_dir.iterdir()]
    assert (
        build_dir / "mainpage.rst"
    ).is_file(), f"mainpage.rst not found.  build dir content: {build_dir_content}"
    assert (build_dir / "mainpage.rst").read_text() == "This is the doc_mainpage.rst"


def _test_copy_license(tmp_path: Path, filename_in: str, filename_out: str) -> None:
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    pkg_dir = tmp_path / "pkg"
    pkg_dir.mkdir()
    license_file = pkg_dir / filename_in
    license_file.write_text("Hello")

    build._copy_license(pkg_dir, build_dir)
    build_dir_content = [str(f.name) for f in build_dir.iterdir()]
    assert (
        build_dir / filename_out
    ).is_file(), f"{filename_out} not found.  build dir content: {build_dir_content}"
    assert (build_dir / filename_out).read_text() == "Hello"


def test_copy_license(tmp_path: Path) -> None:
    _test_copy_license(tmp_path, "LICENSE", "license.txt")


def test_copy_license_txt(tmp_path: Path) -> None:
    _test_copy_license(tmp_path, "license.txt", "license.txt")


def test_copy_license_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        _test_copy_license(tmp_path, "wrong_name", "license.txt")


def test_construct_intersphinx_mapping_config() -> None:
    # empty:
    assert build._construct_intersphinx_mapping_config({}) == "{}"

    # single
    cfg = build._construct_intersphinx_mapping_config({"foo": "https://foo.bar"})
    assert cfg == "{'foo': ('https://foo.bar', None)}"

    # multi
    cfg = build._construct_intersphinx_mapping_config(
        {"foo": "https://foo.bar", "bar": {"target": "bar.com", "inventory": "bar.inv"}}
    )
    assert cfg == "{'foo': ('https://foo.bar', None), 'bar': ('bar.com', 'bar.inv')}"

    # type checks
    with pytest.raises(AssertionError):
        build._construct_intersphinx_mapping_config(
            {42: "foo"}  # type: ignore[dict-item]
        )
    with pytest.raises(AssertionError):
        build._construct_intersphinx_mapping_config(
            {"foo": 42}  # type: ignore[dict-item]
        )
    with pytest.raises(AssertionError):
        build._construct_intersphinx_mapping_config(
            {"foo": {"target": 13, "inventory": "inv"}}  # type: ignore[dict-item]
        )
    with pytest.raises(AssertionError):
        build._construct_intersphinx_mapping_config(
            {"foo": {"target": "url", "inventory": 42}}  # type: ignore[dict-item]
        )


def test_build_documentation_default(tmp_path, ros_pkg_path):
    # just a very basic test if index.html is created
    build.build_documentation(tmp_path, ros_pkg_path, "1.2.3")

    index_html_file = tmp_path / "html/index.html"
    assert index_html_file.exists()
    index_html_content = index_html_file.read_text()
    # verify the mainpage title
    assert "Welcome to ros_pkg’s documentation!" in index_html_content  # noqa[RUF001]
    # verify General Documentation is there
    assert "General Documentation" in index_html_content

    # verify all @VARIABLES@ in indes.rst.in have been substituted
    index_rst_file = tmp_path / "index.rst"
    index_rst_content = index_rst_file.read_text()
    assert "@" not in index_rst_content

    # verify that the PKG symlink was created
    assert (tmp_path / "PKG").is_symlink()
    assert (tmp_path / "PKG" / "package.xml").exists()


def test_build_documentation_mainpage_config(tmp_path, ros_pkg_path, test_configs):
    # just a very basic test if index.html is created
    build.build_documentation(
        tmp_path,
        ros_pkg_path,
        "1.2.3",
        config_file=test_configs / "mainpage_config.toml",
    )

    index_html_file = tmp_path / "html/index.html"
    assert index_html_file.exists()
    index_html_content = index_html_file.read_text()
    # verify the mainpage title
    assert (
        "Welcome to ros_pkg’s documentation!" not in index_html_content  # noqa[RUF001]
    )
    assert "Custom Title" in index_html_content
    # verify General Documentation is not there
    assert "General Documentation" not in index_html_content
