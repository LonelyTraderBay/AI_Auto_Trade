"""Command-line composition root for local operations validation."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol, cast

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from ai_auto_trade.contexts.operations.application.config_validation import (
    ConfigValidationError,
    load_json_yaml_document,
    validate_config_layers,
)


class _SchemaValidator(Protocol):
    """Minimal typed surface needed from jsonschema's validator."""

    def validate(self, instance: object) -> None:
        """Validate one instance or raise a schema validation error."""


def main(argv: Sequence[str] | None = None) -> int:
    """Run the local CLI and return a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command != "config" or args.config_command != "validate":
        parser.error("unsupported command")
    return _validate_config_command(
        Path(args.manifest),
        Path(args.schema),
        Path(args.base),
        Path(args.environment),
    )


def _build_parser() -> argparse.ArgumentParser:
    """Build the supported CLI command tree."""
    parser = argparse.ArgumentParser(prog="ai-auto-trade")
    commands = parser.add_subparsers(dest="command", required=True)
    config = commands.add_parser("config", help="configuration operations")
    config_commands = config.add_subparsers(dest="config_command", required=True)
    validate_parser = config_commands.add_parser("validate", help="validate a local manifest")
    validate_parser.add_argument("--manifest", required=True)
    validate_parser.add_argument(
        "--schema",
        default="contracts/config/deployment-manifest.v1.schema.json",
    )
    validate_parser.add_argument("--base", default="configs/base.yaml")
    validate_parser.add_argument("--environment", default="configs/environments/local.yaml")
    return parser


def _validate_config_command(
    manifest_path: Path,
    schema_path: Path,
    base_path: Path,
    environment_path: Path,
) -> int:
    """Validate config layers and a deployment manifest without external I/O."""
    try:
        effective = validate_config_layers(base_path, environment_path)
        manifest = load_json_yaml_document(manifest_path)
        schema = _load_json_object(schema_path)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        typed_validator = cast(_SchemaValidator, validator)
        typed_validator.validate(manifest)
    except ConfigValidationError as exc:
        print(f"CONFIG_INVALID: {exc}")
        return 2
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"MANIFEST_INVALID: {exc}")
        return 2
    print(
        "CONFIG_VALID: "
        f"manifest={manifest_path} "
        f"environment={effective.get('environment', 'local')} "
        "precedence=base->environment"
    )
    return 0


def _load_json_object(path: Path) -> dict[str, object]:
    """Load a strict JSON schema object from disk."""
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ConfigValidationError(f"schema root must be an object: {path}")
    return cast(dict[str, object], parsed)
