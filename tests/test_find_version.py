import pathlib

import pytest

from breathing_cat import find_version


@pytest.fixture()
def test_pkgs_path() -> pathlib.Path:
    return pathlib.Path(__file__).parent / "test_packages"


def test_find_version_ros(test_pkgs_path):
    pkg_path = test_pkgs_path / "ros_pkg"
    version = find_version.find_version(pkg_path)
    assert version == "1.0.3"


def test_find_version_cmake(test_pkgs_path):
    pkg_path = test_pkgs_path / "cmake_pkg"
    version = find_version.find_version(pkg_path)
    assert version == "3.2.0"


def test_find_version_fail(tmp_path):
    # tmp_path is empty, so no version can be found here
    with pytest.raises(find_version.VersionNotFoundError):
        find_version.find_version(tmp_path)
