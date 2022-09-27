"""Functions for auto-detecting the version of the package."""
import logging
import pathlib
import re
import typing
import xml.etree.ElementTree


_logger = logging.getLogger("breathing_cat.find_version")


class VersionNotFound(Exception):
    pass


def _check_package_xml(package_dir: pathlib.Path) -> typing.Optional[str]:
    """Try to get version from package.xml file."""
    file = package_dir / "package.xml"
    _logger.debug("Check %s", file)
    if file.exists():
        _logger.debug("%s exists", file)

        tree = xml.etree.ElementTree.parse(file)
        root = tree.getroot()
        version = root.find("version")
        if version is not None:
            _logger.info("Found package version %s", version.text)
            return version.text

    return None


def _check_cmakelists(package_dir: pathlib.Path) -> typing.Optional[str]:
    """Try to get project version from CMakeLists.txt."""
    file = package_dir / "CMakeLists.txt"
    _logger.debug("Check %s", file)
    if file.exists():
        _logger.debug("%s exists", file)

        pattern = re.compile(r"\bproject\(.* VERSION (\S+)\b.*\)", re.IGNORECASE)
        with open(file) as f:
            for line in f:
                m = re.search(pattern, line)
                if m:
                    version = m.group(1)
                    _logger.info("Found package version %s", version)
                    return version

    return None


def find_version(package_dir: pathlib.Path) -> str:
    """Try to automatically detect version of the package.

    Args:
        package_dir: Root directory of the package.

    Returns:
        The package version as string.

    Raises:
        VersionNotFound: If no version can be determined for the package.
    """
    # Can be extended by adding more functions to the list.  The functions need to
    # follow the interface `func(package_dir: Path) -> Optional[str]`, returning either
    # a Version string or None, if no version could be found.
    # The first function that returns a version wins, so the order matters!
    for func in [_check_package_xml, _check_cmakelists]:
        version = func(package_dir)
        if version:
            print(f"Found package version: {version}")
            return version

    raise VersionNotFound()
