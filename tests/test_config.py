"""Tests for analysis configuration validation."""

from pathlib import Path

import pytest
import yaml

from spatial_decode.config import load_config
import ast

from spatial_decode.config import ALLOWED_KEYS

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "config" / "default.yaml"


def test_default_config_is_valid():
    """All parameters in the default configuration are accepted."""
    with DEFAULT_CONFIG.open() as f:
        expected = yaml.safe_load(f)

    config = load_config(DEFAULT_CONFIG)

    assert config == expected


@pytest.mark.parametrize(
    "unknown_parameter",
    [
        "bin_size",
        "smoothing_raduis",
        "unknown_parameter",
        "random_seed",
    ],
)
def test_unknown_config_parameter_is_rejected(
    tmp_path,
    unknown_parameter,
):
    """An unknown configuration parameter must raise an error."""
    with DEFAULT_CONFIG.open() as f:
        config = yaml.safe_load(f)

    config[unknown_parameter] = 10

    config_path = tmp_path / "invalid_config.yaml"

    config_path.write_text(yaml.safe_dump(config))

    with pytest.raises(
        ValueError,
        match=unknown_parameter,
    ):
        load_config(config_path)


def test_multiple_unknown_parameters_are_reported(tmp_path):
    """The error should identify all unknown parameters."""
    with DEFAULT_CONFIG.open() as f:
        config = yaml.safe_load(f)

    config["unknown_one"] = 1
    config["unknown_two"] = 2

    config_path = tmp_path / "invalid_config.yaml"

    config_path.write_text(yaml.safe_dump(config))

    with pytest.raises(ValueError) as error:
        load_config(config_path)

    assert "unknown_one" in str(error.value)
    assert "unknown_two" in str(error.value)


def test_modified_known_parameters_are_accepted(tmp_path):
    """Users must be able to change recognized parameters."""
    with DEFAULT_CONFIG.open() as f:
        config = yaml.safe_load(f)

    config["bin_size_um"] = 16
    config["smoothing_radius"] = 1

    config_path = tmp_path / "custom_config.yaml"

    config_path.write_text(yaml.safe_dump(config))

    loaded = load_config(config_path)

    assert loaded["bin_size_um"] == 16
    assert loaded["smoothing_radius"] == 1


@pytest.mark.parametrize(
    "correct_key, misspelled_key",
    [
        ("seed", "sead"),
        ("bin_size_um", "bin_szie_um"),
        ("n_domains", "n_domians"),
        ("smoothing_radius", "smoothing_raduis"),
        ("kmeans_n_init", "kmeans_n_int"),
    ],
)
def test_misspelled_config_key_is_rejected(
    tmp_path,
    correct_key,
    misspelled_key,
):
    """Misspelled configuration keys must not be silently accepted."""
    config = yaml.safe_load(DEFAULT_CONFIG.read_text())

    # Replace a valid parameter with a misspelled version.
    config[misspelled_key] = config.pop(correct_key)

    config_path = tmp_path / "misspelled_config.yaml"
    config_path.write_text(yaml.safe_dump(config))

    with pytest.raises(ValueError, match=misspelled_key):
        load_config(config_path)


def test_default_config_has_correct_parameter_names():
    """The default configuration must contain exactly the supported keys."""
    expected_keys = {
        "seed",
        "bin_size_um",
        "n_domains",
        "smoothing_radius",
        "kmeans_n_init",
    }

    config = yaml.safe_load(DEFAULT_CONFIG.read_text())
    actual_keys = set(config)

    unknown_keys = actual_keys - expected_keys
    missing_keys = expected_keys - actual_keys

    assert actual_keys == expected_keys, (
        f"Unknown parameters: {sorted(unknown_keys)}; "
        f"Missing parameters: {sorted(missing_keys)}"
    )


@pytest.mark.parametrize(
    "missing_key",
    [
        "seed",
        "bin_size_um",
        "n_domains",
        "smoothing_radius",
        "kmeans_n_init",
    ],
)
def test_missing_required_parameter_is_rejected(
    tmp_path,
    missing_key,
):
    """Every required configuration parameter must be provided."""

    config = yaml.safe_load(DEFAULT_CONFIG.read_text())
    config.pop(missing_key)

    config_path = tmp_path / "missing_parameter.yaml"
    config_path.write_text(yaml.safe_dump(config))

    with pytest.raises(ValueError, match=missing_key):
        load_config(config_path)


@pytest.mark.parametrize(
    "invalid_content",
    [
        "",
        "null",
        "42",
        "- seed\n- bin_size_um",
    ],
)
def test_invalid_configuration_structure_is_rejected(
    tmp_path,
    invalid_content,
):
    """The configuration must be a mapping of keys to values."""

    config_path = tmp_path / "invalid_structure.yaml"
    config_path.write_text(invalid_content)

    with pytest.raises(ValueError, match="YAML mapping"):
        load_config(config_path)


def test_non_string_parameter_is_rejected(tmp_path):
    """Parameter names must be strings."""

    config_path = tmp_path / "invalid_key.yaml"
    config_path.write_text("123: 8")

    with pytest.raises(ValueError, match="keys must be strings"):
        load_config(config_path)


def test_source_code_uses_only_declared_config_keys():
    """Configuration keys accessed by source code must be declared."""

    source_dir = Path(__file__).resolve().parents[1] / "src" / "spatial_decode"

    unknown_keys = []

    for path in sorted(source_dir.rglob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))

        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Subscript)
                and isinstance(node.value, ast.Name)
                and node.value.id == "config"
                and isinstance(node.slice, ast.Constant)
                and isinstance(node.slice.value, str)
            ):
                key = node.slice.value

                if key not in ALLOWED_KEYS:
                    unknown_keys.append(f"{path.name}:{node.lineno}: {key}")

    assert not unknown_keys, "Undeclared configuration parameters:\n" + "\n".join(
        unknown_keys
    )
