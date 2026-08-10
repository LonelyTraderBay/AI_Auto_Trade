# Task 0.2 — Guardrails Evidence

| Field | Value |
|---|---|
| Task ID | 0.2 |
| UTC Timestamp | 2026-08-06T13:18:48Z |
| Proposed status | REVIEW |

## Required Commands

| Command | Exit code |
|---|---|
| uv sync --locked | 0 |
| uv run ruff format --check . | 0 |
| uv run ruff check . | 0 |
| uv run pyright | 0 |
| uv run pytest | 0 |
| uv run python scripts/validate_contracts.py | 0 |

## Files created/modified

| File | Action |
|---|---|
| tasks/active/0.2-guardrails.yaml | Created — Task 0.2 card |
| pyproject.toml | Modified — added hypothesis==6.165.2, import-linter==2.13, jsonschema==4.26.0 (exact pins) |
| uv.lock | Updated — regenerated after dep additions |
| .importlinter | Created — domain-no-framework contract with include_external_packages=True |
| tests/architecture/__init__.py | Created — empty, per ENG-REPO-001 §2a |
| tests/architecture/test_import_boundaries.py | Created — boundary test via importlinter.cli |
| scripts/validate_contracts.py | Created — validates all .schema.json via jsonschema Draft202012Validator |
| .github/workflows/ci.yml | Created — CI workflow running full required_commands profile |

## Test results

4 passed (3 bootstrap unit tests + 1 architecture boundary test)

## Contract validation

14 schema files validated — all OK.

## Pinned versions added

- hypothesis==6.165.2
- import-linter==2.13
- jsonschema==4.26.0

## Proposed status: REVIEW
