import pathlib
import shutil
from copy import deepcopy

import pytest

from breathing_cat import config


@pytest.fixture
def test_data():
    return pathlib.Path(__file__).parent / "config"


def test_update_recursive():
    """Test various cases of ``update_recursive``."""
    d1 = {
        "foo": 42,
        "bar": {"one": 1, "two": 2},
    }
    u1 = {
        "foo": 13,
        "bar": {"two": 3},
    }
    u2 = {
        "bar": {"three": 3},
        "baz": 23,
    }

    # Note: first argument is updated in place, so pass copies here
    assert config.update_recursive(deepcopy(d1), {}) == d1
    assert config.update_recursive({}, d1) == d1
    assert config.update_recursive(deepcopy(d1), u1) == {
        "foo": 13,
        "bar": {"one": 1, "two": 3},
    }
    assert config.update_recursive(deepcopy(d1), u2) == {
        "foo": 42,
        "bar": {"one": 1, "two": 2, "three": 3},
        "baz": 23,
    }


def test_find_config_file_at_root(tmp_path: pathlib.Path):
    """Test find_config_file with config file at root of search directory."""
    cfg_file = tmp_path / config._CONFIG_FILE_NAME
    cfg_file.touch()

    found_file = config.find_config_file(tmp_path)
    assert found_file == cfg_file


def test_find_config_file_in_doc(tmp_path: pathlib.Path):
    """Test find_config_file with config file in <package>/doc."""
    path = tmp_path / "doc"
    cfg_file = path / config._CONFIG_FILE_NAME
    path.mkdir()
    cfg_file.touch()

    found_file = config.find_config_file(tmp_path)
    assert found_file == cfg_file


def test_find_config_file_in_docs(tmp_path: pathlib.Path):
    """Test find_config_file with config file in <package>/docs."""
    path = tmp_path / "docs"
    cfg_file = path / config._CONFIG_FILE_NAME
    path.mkdir()
    cfg_file.touch()

    found_file = config.find_config_file(tmp_path)
    assert found_file == cfg_file


def test_find_config_file_none(tmp_path: pathlib.Path):
    """Test find_config_file with no file to be found."""
    with pytest.raises(FileNotFoundError):
        config.find_config_file(tmp_path)


def test_load_config_not_found():
    """Test load_config if non-existent file is passed."""
    with pytest.raises(FileNotFoundError):
        config.load_config("/does/for/sure/not/exists.toml")


def test_load_config(test_data):
    """Test loading a config file with load_config()."""
    cfg = config.load_config(test_data / "config1.toml")
    assert cfg["doxygen"]["exclude_patterns"][0] == "config1"


def test_find_and_load_config(tmp_path, test_data):
    """Test finding and loading a config file."""
    # copy test config to tmp_path
    cfg_file = test_data / "config1.toml"
    shutil.copyfile(cfg_file, tmp_path / config._CONFIG_FILE_NAME)

    cfg = config.find_and_load_config(tmp_path)
    assert cfg["doxygen"]["exclude_patterns"][0] == "config1"
