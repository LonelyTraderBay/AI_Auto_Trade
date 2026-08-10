"""Architecture boundary tests — Task 0.2 (extended Task 0.4).

Enforces that domain/application layers do not import framework/vendor packages
and that layer dependency rules are respected per ADR-0002.

Refs: ADR-0001, ADR-0002, ADR-0014
"""

import subprocess
import sys


def _run_lint_imports() -> subprocess.CompletedProcess[str]:
    """Run import-linter and return the result.

    Returns:
        Completed process with stdout/stderr captured.
    """
    return subprocess.run(
        [sys.executable, "-m", "importlinter.cli"],
        capture_output=True,
        text=True,
        check=False,
    )


def test_domain_no_framework_imports() -> None:
    """Domain modules must not import FastAPI, SQLAlchemy, Pydantic or vendor SDKs.

    Runs import-linter against the domain-no-framework contract. With the
    Task 0.1 skeleton all domain modules are empty so this always passes.
    Any future domain import of a forbidden package will fail this test —
    that is the intended safety behavior.
    """
    result = _run_lint_imports()
    assert result.returncode == 0, (
        f"Import boundary violation — domain-no-framework:\n{result.stdout}\n{result.stderr}"
    )


def test_application_no_adapter_imports() -> None:
    """Application layer must not import concrete adapter implementations.

    Application uses ports (protocols/interfaces) only; adapters are wired
    exclusively at the composition root in apps/. Enforced by ADR-0002.
    """
    result = _run_lint_imports()
    assert result.returncode == 0, (
        f"Import boundary violation — app-no-adapter:\n{result.stdout}\n{result.stderr}"
    )


def test_domain_no_application_imports() -> None:
    """Domain layer must not import application or adapter layers.

    Domain purity (pure Python/stdlib + shared_kernel) is a safety control:
    it guarantees deterministic replay and testability without framework.
    Enforced by ADR-0002.
    """
    result = _run_lint_imports()
    assert result.returncode == 0, (
        f"Import boundary violation — domain-no-application:\n{result.stdout}\n{result.stderr}"
    )


def test_all_import_contracts_pass() -> None:
    """All import-linter contracts must pass simultaneously.

    Single authoritative check that runs the full .importlinter configuration.
    Individual tests above document which contract each one targets.
    """
    result = _run_lint_imports()
    assert result.returncode == 0, (
        f"One or more import-linter contracts failed:\n{result.stdout}\n{result.stderr}"
    )
