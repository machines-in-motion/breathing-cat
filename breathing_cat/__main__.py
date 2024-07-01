"""Script to run breathing cat."""

import argparse
import logging
import pathlib
import sys
import textwrap

from . import __version__, find_version
from .build import build_documentation


def main() -> int:
    """Use breathing-cat to build documentation of a C++/Python package."""

    def absolute_path(path: str) -> pathlib.Path:
        return pathlib.Path(path).absolute()

    parser = argparse.ArgumentParser(
        description=textwrap.dedent(
            """
            Use breathing-cat to build documentation of a C++/Python package.

            Copyright (c) 2022 New York University and Max Planck Gesellschaft.
            License: BSD 3-clause

            For more information see https://github.com/machines-in-motion/breathing-cat
            """
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        help="Show version of breathing-cat.",
        version=f"breathing-cat version {__version__}",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        required=True,
        type=absolute_path,
        metavar="DIRECTORY",
        help="Build directory",
    )
    parser.add_argument(
        "--package-dir",
        "-p",
        required=True,
        type=absolute_path,
        metavar="DIRECTORY",
        help="Package directory",
    )
    parser.add_argument(
        "--python-dir",
        type=absolute_path,
        metavar="DIRECTORY",
        help="""Directory containing the Python package.  If not set, it is
            auto-detected inside the package directory
        """,
    )
    parser.add_argument(
        "--package-version",
        type=str,
        help="""Package version that is shown in the documentation (something like
            '1.42.0').  If not set, breathing-cat tries to auto-detect it by looking
            for files like package.xml in the package directory.
        """,
    )
    parser.add_argument(
        "--skip-cpp", action="store_true", help="Do not include C++ API documentation."
    )
    parser.add_argument(
        "--skip-python",
        action="store_true",
        help="Do not include Python API documentation.",
    )
    parser.add_argument(
        "--skip-cmake",
        action="store_true",
        help="Do not include CMake API documentation.",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Do not ask before deleting files.",
    )
    parser.add_argument(
        "--config",
        type=absolute_path,
        metavar="FILE",
        help="""Path to config file.  If not set explicitly, bcat searches for a file
            'breathing_cat.toml' in the package directory.
        """,
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug output.")
    args = parser.parse_args()

    if args.verbose:
        logger_level = logging.DEBUG
    else:
        logger_level = logging.INFO
    logging.basicConfig(level=logger_level)

    if not args.force and args.output_dir.exists():
        print(
            "Output directory {} already exists."
            " It will be deleted if you proceed!".format(args.output_dir)
        )
        c = input("Continue? [y/N] ")

        if c not in ["y", "Y", "yes"]:
            print("Abort.")
            return 1

    if not args.package_version:
        try:
            args.package_version = find_version.find_version(args.package_dir)
        except find_version.VersionNotFoundError:
            print(
                "ERROR: Package version could not be determined."
                "  Please specify it using --package-version."
            )
            return 1

    build_documentation(
        args.output_dir,
        args.package_dir,
        args.package_version,
        python_pkg_path=args.python_dir,
        config_file=args.config,
        skip_cpp=args.skip_cpp,
        skip_python=args.skip_python,
        skip_cmake=args.skip_cmake,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
