"""Deterministic validation helpers for local JSON-compatible YAML config."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import cast


class ConfigValidationError(ValueError):
    """Raised when a local configuration document violates a safety rule."""


def load_json_yaml_document(path: Path) -> dict[str, object]:
    """Load a JSON-compatible YAML document with duplicate-key rejection.

    JSON is a strict subset of YAML 1.2. Phase 0 uses this subset so the
    validator remains deterministic without an unapproved YAML dependency.

    Args:
        path: Repository-relative config path.

    Returns:
        Parsed object document.

    Raises:
        ConfigValidationError: If the document is not an object or is invalid.
    """
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_object_pairs)
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigValidationError(f"invalid JSON-compatible YAML: {path}") from exc
    if not isinstance(parsed, dict):
        raise ConfigValidationError(f"configuration root must be an object: {path}")
    return cast(dict[str, object], parsed)


def validate_config_layers(base_path: Path, environment_path: Path) -> dict[str, object]:
    """Validate base/environment precedence and return the effective config.

    Args:
        base_path: Base configuration path.
        environment_path: Environment overlay path.

    Returns:
        Recursively merged effective configuration.

    Raises:
        ConfigValidationError: If a layer contains unsafe or unsupported keys.
    """
    base = load_json_yaml_document(base_path)
    environment = load_json_yaml_document(environment_path)
    _validate_layer(base, "base")
    _validate_layer(environment, "environment")
    _reject_forbidden_overrides(environment)
    return _merge_mappings(base, environment)


def _object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Build an object while rejecting duplicate semantic keys."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ConfigValidationError(f"duplicate configuration key: {key}")
        result[key] = value
    return result


def _validate_layer(document: Mapping[str, object], layer_name: str) -> None:
    """Validate common layer invariants and reject secret-like fields."""
    config_version = document.get("config_version")
    if config_version != 1:
        raise ConfigValidationError(f"{layer_name}.config_version must be 1")
    _reject_secret_like_fields(document, layer_name)


def _reject_secret_like_fields(document: Mapping[str, object], path: str) -> None:
    """Reject secret-bearing keys recursively in local config."""
    forbidden_fragments = ("secret", "password", "token", "api_key", "credential")
    for key, value in document.items():
        key_path = f"{path}.{key}"
        if any(fragment in key.lower() for fragment in forbidden_fragments):
            raise ConfigValidationError(f"secret-like key is not allowed: {key_path}")
        if isinstance(value, Mapping):
            _reject_secret_like_fields(cast(Mapping[str, object], value), key_path)
        elif isinstance(value, list):
            items = cast(list[object], value)
            for index, item in enumerate(items):
                if isinstance(item, Mapping):
                    _reject_secret_like_fields(
                        cast(Mapping[str, object], item), f"{key_path}[{index}]"
                    )


def _reject_forbidden_overrides(environment: Mapping[str, object]) -> None:
    """Prevent environment config from changing safety-owned sections."""
    forbidden_sections = {"risk", "strategy", "execution", "venue", "venues", "ai"}
    overridden = sorted(forbidden_sections.intersection(environment))
    if overridden:
        joined = ", ".join(overridden)
        raise ConfigValidationError(f"environment cannot override safety-owned sections: {joined}")


def _merge_mappings(base: Mapping[str, object], overlay: Mapping[str, object]) -> dict[str, object]:
    """Merge maps recursively; later scalar/list values replace earlier values."""
    merged = dict(base)
    for key, value in overlay.items():
        previous = merged.get(key)
        if isinstance(previous, Mapping) and isinstance(value, Mapping):
            merged[key] = _merge_mappings(
                cast(Mapping[str, object], previous), cast(Mapping[str, object], value)
            )
        else:
            merged[key] = value
    return merged
