"""Functions for loading analysis configuration."""

from pathlib import Path

import yaml


def load_config(config_path):
    """Load analysis parameters from a YAML configuration file."""
    config_path = Path(config_path).expanduser()
    return yaml.safe_load(config_path.read_text())
