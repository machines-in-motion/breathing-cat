import os
import pathlib
import typing

import variconf
from omegaconf import OmegaConf


PathLike = typing.Union[str, os.PathLike]


_CONFIG_FILE_NAME = "breathing_cat.toml"

_DEFAULT_CONFIG: typing.Dict[str, typing.Any] = {
    "PACKAGE_DIR": "{{PACKAGE_DIR}}",  # for compatibility of deprecated ${PACKAGE_DIR}
    "doxygen": {
        "exclude_patterns": [],
    },
    "intersphinx": {"mapping": {}},
}


def _get_config_loader() -> variconf.WConf:
    return variconf.WConf(_DEFAULT_CONFIG, strict=False)


def config_from_dict(config: dict) -> dict:
    """Get the default configuration."""
    config_loader = _get_config_loader()
    config_loader.load_dict(config)

    return typing.cast(dict, OmegaConf.to_container(config_loader.get(), resolve=True))


def load_config(config_file: PathLike) -> dict:
    """Load configuration from the given TOML file.

    Load the configuration from the given TOML file (using default values for parameters
    not specified in the file).

    Args:
        config_file: Path to the config file.

    Returns:
        Configuration.
    """
    config_loader = _get_config_loader()
    config_loader.load_file(config_file)

    return typing.cast(dict, OmegaConf.to_container(config_loader.get(), resolve=True))


def find_and_load_config(
    package_dir: PathLike, config_file_name: str = _CONFIG_FILE_NAME
) -> dict:
    """Find and load config file.  If none is found, return default config.

    See :func:`find_config_file` for possible file locations that are checked.

    Args:
        package_dir: Directory in which to search for the config file.
        config_file_name: Name of the file to search for.

    Returns:
        Configuration.
    """
    package_dir = pathlib.PurePath(package_dir)
    search_paths = [package_dir, package_dir / "doc", package_dir / "docs"]

    config_loader = _get_config_loader()
    config_loader.load_file(
        config_file_name, search_paths=search_paths, fail_if_not_found=False
    )

    return typing.cast(dict, OmegaConf.to_container(config_loader.get(), resolve=True))
