import pathlib
import shutil

import pytest

from breathing_cat import config


@pytest.fixture()
def test_data():
    return pathlib.Path(__file__).parent / "config"


def test_load_config_not_found():
    """Test load_config if non-existent file is passed."""
    with pytest.raises(FileNotFoundError):
        config.load_config("/does/for/sure/not/exists.toml")


def test_load_config(test_data):
    """Test loading a config file with load_config()."""
    cfg = config.load_config(test_data / "config1.toml")
    assert cfg["doxygen"]["exclude_patterns"][0] == "config1"


def test_config_from_dict_intersphinx():
    """Test loading a config file with load_config()."""
    cfg = config.config_from_dict(
        {
            "intersphinx": {
                "mapping": {
                    "long": {"target": "docs.foo.org", "inventory": "my_inv.txt"},
                    "short": "docs.foo.org",
                }
            },
        }
    )
    assert cfg["intersphinx"]["mapping"] == {
        "long": {"target": "docs.foo.org", "inventory": "my_inv.txt"},
        "short": "docs.foo.org",
    }


def test_load_config_intersphinx(test_data):
    """Test loading a config file with load_config()."""
    cfg = config.load_config(test_data / "config_intersphinx.toml")
    assert cfg["intersphinx"]["mapping"] == {
        "long": {"target": "docs.foo.org", "inventory": "my_inv.txt"},
        "short": "docs.foo.org",
    }


def test_find_and_load_config_intersphinx(test_data):
    """Test loading a config file with load_config()."""
    cfg = config.find_and_load_config(test_data, "config_intersphinx.toml")
    assert cfg["intersphinx"]["mapping"] == {
        "long": {"target": "docs.foo.org", "inventory": "my_inv.txt"},
        "short": "docs.foo.org",
    }


def test_config_from_dict_mainpage():
    """Test loading a config file with load_config()."""
    cfg1 = config.config_from_dict({})
    assert cfg1["mainpage"] == {
        "title": None,
        "auto_general_docs": True,
    }

    cfg2 = config.config_from_dict(
        {
            "mainpage": {
                "title": "Custom Title",
                "auto_general_docs": False,
            },
        }
    )
    assert cfg2["mainpage"] == {
        "title": "Custom Title",
        "auto_general_docs": False,
    }


def _setup_pkg_dir_with_config(config_location, tmp_path, test_data):
    """Helper for the test_find_and_load_config_* functions."""
    # create target directory
    target_dir = tmp_path / config_location
    target_dir.mkdir(exist_ok=True)
    # copy config file from test data to target location
    shutil.copyfile(
        test_data / "config1.toml",
        target_dir / config._CONFIG_FILE_NAME,
    )

    return tmp_path


def test_find_and_load_config_from_root(tmp_path, test_data):
    """Test finding and loading a config file."""
    pkg_path = _setup_pkg_dir_with_config(".", tmp_path, test_data)

    cfg = config.find_and_load_config(pkg_path)
    assert cfg["doxygen"]["exclude_patterns"][0] == "config1"


def test_find_and_load_config_from_doc(tmp_path, test_data):
    """Test finding and loading a config file."""
    pkg_path = _setup_pkg_dir_with_config("doc", tmp_path, test_data)

    cfg = config.find_and_load_config(pkg_path)
    assert cfg["doxygen"]["exclude_patterns"][0] == "config1"


def test_find_and_load_config_from_docs(tmp_path, test_data):
    """Test finding and loading a config file."""
    pkg_path = _setup_pkg_dir_with_config("docs", tmp_path, test_data)

    cfg = config.find_and_load_config(pkg_path)
    assert cfg["doxygen"]["exclude_patterns"][0] == "config1"


def test_find_and_load_config_invalid_location(tmp_path, test_data):
    """Test finding and loading a config file."""
    pkg_path = _setup_pkg_dir_with_config("this_is_wrong", tmp_path, test_data)

    cfg = config.find_and_load_config(pkg_path)
    assert cfg == config._DEFAULT_CONFIG
