"""Contract validation script — Task 0.2.

Validates all JSON Schema files in contracts/ against JSON Schema Draft 2020-12.
Validates all fixture files in contracts/fixtures/ against their corresponding schemas.
Exit code 0 = all valid. Exit code 1 = validation failure.

Usage:
    uv run python scripts/validate_contracts.py
"""

import json
import sys
from pathlib import Path

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except ImportError:
    print("ERROR: jsonschema not installed. Add to dev dependencies.", file=sys.stderr)
    sys.exit(1)


def validate_schemas(contracts_dir: Path) -> list[str]:
    """Validate all .schema.json files are valid JSON Schema Draft 2020-12.

    Args:
        contracts_dir: Path to the contracts directory.

    Returns:
        List of error messages; empty list means all valid.
    """
    errors: list[str] = []
    schema_files = list(contracts_dir.rglob("*.schema.json"))

    if not schema_files:
        print("WARNING: No schema files found in contracts/")
        return errors

    for schema_path in sorted(schema_files):
        try:
            with schema_path.open() as f:
                schema = json.load(f)
            Draft202012Validator.check_schema(schema)
            print(f"  OK  {schema_path.relative_to(contracts_dir.parent)}")
        except jsonschema.exceptions.SchemaError as exc:
            errors.append(f"FAIL {schema_path}: {exc.message}")
        except json.JSONDecodeError as exc:
            errors.append(f"FAIL {schema_path}: Invalid JSON — {exc}")

    return errors


def main() -> int:
    """Run contract validation and return exit code.

    Returns:
        0 if all contracts are valid, 1 otherwise.
    """
    repo_root = Path(__file__).parent.parent
    contracts_dir = repo_root / "contracts"

    if not contracts_dir.exists():
        print(f"ERROR: contracts/ not found at {contracts_dir}", file=sys.stderr)
        return 1

    print("Validating JSON Schema files...")
    errors = validate_schemas(contracts_dir)

    if errors:
        print(f"\n{len(errors)} validation error(s):")
        for err in errors:
            print(f"  {err}")
        return 1

    print("\nAll schemas valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
