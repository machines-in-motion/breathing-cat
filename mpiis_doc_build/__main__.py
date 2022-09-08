import argparse
import pathlib

from .build import build_documentation


def main():
    def AbsolutePath(path):
        return pathlib.Path(path).absolute()

    parser = argparse.ArgumentParser(description=__doc__)
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
    parser.add_argument(
        "--project-version", required=True, type=str, help="Package version"
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Do not ask before deleting files.",
    )
    args = parser.parse_args()

    if not args.force and args.output_dir.exists():
        print(
            "Output directory {} already exists."
            " It will be deleted if you proceed!".format(args.output_dir)
        )
        c = input("Continue? [y/N] ")

        if c not in ["y", "Y", "yes"]:
            print("Abort.")
            return

    build_documentation(
        args.output_dir,
        args.package_dir,
        args.project_version,
        python_pkg_path=args.python_dir,
    )


if __name__ == "__main__":
    main()
