"""
Safe configuration file storage for locspoof.
Uses standard OS directories and enforces atomic, secure file writes.
"""

import json
import os
from pathlib import Path
from typing import Optional
from platformdirs import user_config_dir

from locspoof.config.settings import Config
from locspoof.core.exceptions import ConfigurationError
from locspoof.utils.logger import logger


def get_config_dir() -> Path:
    return Path(user_config_dir("locspoof"))


def get_config_path() -> Path:
    return get_config_dir() / "config.json"


def load_config() -> Config:
    """Load configuration from disk. Returns default Config if file does not exist."""
    path = get_config_path()
    if not path.exists():
        return Config()

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Config.model_validate(data)
    except json.JSONDecodeError as exc:
        raise ConfigurationError(
            message=f"Configuration file at '{path}' is corrupted or invalid JSON.",
            detail=str(exc),
            suggestion=f"You can delete or inspect '{path}'.",
        ) from exc
    except Exception as exc:
        raise ConfigurationError(
            message=f"Failed to read configuration from '{path}'.",
            detail=str(exc),
            suggestion="Verify file permissions.",
        ) from exc


def save_config(config: Config) -> Path:
    """
    Save configuration atomically with restricted file permissions (0600).
    """
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    target_path = get_config_path()
    temp_path = config_dir / f".tmp_{os.getpid()}_config.json"

    try:
        # Write to temp file first
        content = config.model_dump_json(indent=2)
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Set restrictive permissions (user read/write only)
        os.chmod(temp_path, 0o600)
        # Atomic rename
        temp_path.replace(target_path)
        logger.debug(f"Configuration saved to '{target_path}'")
        return target_path
    except Exception as exc:
        if temp_path.exists():
            temp_path.unlink()
        raise ConfigurationError(
            message=f"Failed to save configuration to '{target_path}'.",
            detail=str(exc),
            suggestion="Ensure write permissions in the user config directory.",
        ) from exc
