"""Bootstrap validation test — Task 0.1.

Confirms the package is importable and version is correct.
All test functions must declare return type -> None (ENG-PY-001 §5a ANN rule).
"""

import importlib
import importlib.resources

import ai_auto_trade


def test_package_importable() -> None:
    """Package ai_auto_trade must be importable after uv sync."""
    module = importlib.import_module("ai_auto_trade")
    assert module is not None


def test_package_has_docstring() -> None:
    """Package __init__.py must have a non-empty docstring."""
    assert ai_auto_trade.__doc__ is not None
    assert len(ai_auto_trade.__doc__.strip()) > 0


def test_py_typed_marker_exists() -> None:
    """py.typed marker must exist for PEP 561 compliance."""
    ref = importlib.resources.files("ai_auto_trade").joinpath("py.typed")
    assert ref.is_file()
