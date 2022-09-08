import argparse
import logging
import pathlib
import sys

from . import __version__, find_version
from .build import build_documentation


def main():
    def AbsolutePath(path):
        return pathlib.Path(path).absolute()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        action="version",
        help="Show version of mpiis_doc_build.",
        version=f"mpiis_doc_build version {__version__}",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=AbsolutePath,
        help="Build directory",
    )
    parser.add_argument(
        "--package-dir",
        required=True,
        type=AbsolutePath,
        help="Package directory",
    )
    parser.add_argument(
        "--python-dir",
        type=AbsolutePath,
        help="""Directory containing the Python package.  If not set, it is
            auto-detected inside the package directory
        """,
    )
    parser.add_argument("--project-version", type=str, help="Package version")
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Do not ask before deleting files.",
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

    if not args.project_version:
        try:
            args.project_version = find_version.find_version(args.package_dir)
        except find_version.VersionNotFound:
            print(
                "ERROR: Package version could not be determined."
                "  Please specify it using --package-version."
            )
            return 1

    build_documentation(
        args.output_dir,
        args.package_dir,
        args.project_version,
        python_pkg_path=args.python_dir,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
