import collections.abc
import copy
import os
import pathlib
import typing

import tomli


PathLike = typing.Union[str, os.PathLike]


_CONFIG_FILE_NAME = "breathing_cat.toml"

_DEFAULT_CONFIG: typing.Dict[str, typing.Any] = {
    "doxygen": {
        "exclude_patterns": [],
    },
    "intersphinx": {"mapping": {}},
}


def update_recursive(d, u):
    """Recursively update values in d with values from u."""
    # From https://stackoverflow.com/a/3233356/2095383 (CC BY-SA 4.0)
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update_recursive(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def find_config_file(
    package_dir: PathLike,
) -> pathlib.Path:
    """Find config file in the given package directory.

    Searches for a config file in the following places (in this order):

    - <package_dir>/breathing_cat.toml
    - <package_dir>/doc/breathing_cat.toml
    - <package_dir>/docs/breathing_cat.toml

    The first file found is returned.

    Args:
        package_dir: Directory in which to search for the file.

    Returns:
        Path to the first config file that was found.

    Raises:
        FileNotFoundError: If no config file is found.
    """
    package_dir = pathlib.Path(package_dir)
    search_paths = (".", "doc", "docs")

    for search_path in search_paths:
        path = package_dir / search_path / _CONFIG_FILE_NAME
        if path.is_file():
            return path

    concat_paths = ",".join(search_paths)
    raise FileNotFoundError(
        f"No file {_CONFIG_FILE_NAME} found in {package_dir}/{{{concat_paths}}}"
    )


def load_config(config_file: PathLike) -> dict:
    """Load configuration from the given TOML file.

    Load the configuration from the given TOML file (using default values for parameters
    not specified in the file).

    Args:
        config_file: Path to the config file.

    Returns:
        Configuration dictionary.
    """
    config = copy.deepcopy(_DEFAULT_CONFIG)

    with open(config_file, "rb") as f:
        user_config = tomli.load(f)
    config = update_recursive(config, user_config)

    return config


def find_and_load_config(package_dir: PathLike) -> dict:
    """Find and load config file.  If none is found, return default config.

    See :func:`find_config_file` for possible file locations that are checked.

    Args:
        package_dir: Directory in which to search for the config file.

    Returns:
        Configuration.
    """
    try:
        config_file = find_config_file(package_dir)
        config = load_config(config_file)
        return config
    except FileNotFoundError:
        # if config file is not found, simply return the default config
        return copy.deepcopy(_DEFAULT_CONFIG)
