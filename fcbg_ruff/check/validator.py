from __future__ import annotations

from typing import TYPE_CHECKING

from ..utils._checks import ensure_path
from ._regex import validate_file_name, validate_folder_name

if TYPE_CHECKING:
    from pathlib import Path


def validate_folder(folder: Path) -> dict[str, dict[Path, list[int]]]:
    """Validate a folder from the documentary system and its content recursively.

    Parameters
    ----------
    folder : Path
        Path to the folder to validate.

    Returns
    -------
    violations : dict
        Dictionary of primary and secondary violations found.
    """
    folder = ensure_path(folder, must_exist=True)
    violations = {"primary": dict(), "secondary": dict()}
    _validate_folder(folder, violations)
    return violations


def _validate_folder(
    folder: Path, violations: dict[str, dict[Path, list[int]]]
) -> None:
    """Validate a folder and its content recursively.

    Parameters
    ----------
    folder : Path
        Path to the folder to validate.
    violations : dict
        Dictionary of primary and secondary violations found.
    """
    errors = validate_folder_name(folder)
    for key in ("primary", "secondary"):
        if len(errors[key]) != 0:
            violations[key][folder] = errors[key]
    for elt in folder.iterdir():
        if elt.is_dir() and elt.name == "__old":
            pass
        elif elt.is_dir():
            _validate_folder(elt, violations)
        else:
            errors = validate_file_name(elt)
            for key in ("primary", "secondary"):
                if len(errors[key]) != 0:
                    violations[key][elt] = errors[key]
