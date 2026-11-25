"""Functions for loading and validating analysis configuration."""

from difflib import get_close_matches
from pathlib import Path

import yaml


ALLOWED_KEYS = frozenset(
    {
        "seed",
        "bin_size_um",
        "n_domains",
        "smoothing_radius",
        "kmeans_n_init",
    }
)


def validate_config(config):
    """Reject unknown, misspelled or missing configuration keys."""

    if not isinstance(config, dict):
        raise ValueError("Configuration must be a YAML mapping")

    if not all(isinstance(key, str) for key in config):
        raise ValueError("Configuration keys must be strings")

    supplied_keys = set(config)

    unknown_keys = supplied_keys - ALLOWED_KEYS
    missing_keys = ALLOWED_KEYS - supplied_keys

    errors = []

    for key in sorted(unknown_keys):
        message = f"Unknown configuration parameter: '{key}'."

        matches = get_close_matches(
            key,
            sorted(ALLOWED_KEYS),
            n=1,
            cutoff=0.6,
        )

        if matches:
            message += f" Did you mean '{matches[0]}'?"

        errors.append(message)

    if missing_keys:
        errors.append(
            "Missing required configuration parameters: "
            + ", ".join(sorted(missing_keys))
        )

    if errors:
        raise ValueError("\n".join(errors))


def load_config(config_path):
    """Load and validate analysis parameters from a YAML file."""

    config_path = Path(config_path).expanduser()
    config = yaml.safe_load(config_path.read_text())

    validate_config(config)

    return config
