from __future__ import annotations

import string
from datetime import datetime
from typing import TYPE_CHECKING

from .config import _FORBIDDEN_STEM_CHARACTERS, _USERCODE_LENGTH

if TYPE_CHECKING:
    from pathlib import Path


def _validate_folder(folder: Path, violations: dict[Path, int]):
    """Validate a folder and its content.

    This function recursively calls itself on subfolders.

    Parameters
    ----------
    folder : Path
        Full path to the folder to validate.
    violations : dict
        Dictionary of already found violation. The dictionary is modified in-place by
        each recursive call.

    Returns
    -------
    violations : dict
        Dictionary of violations found in the folder and its content.
    """
    violations = dict() if violations is None else violations
    folders = []  # list folders to validate last code letter consecutiveness
    for elt in folder.iterdir():
        if elt.is_dir() and elt != "__old":
            folders.append(elt)
            err_code = _validate_folder_name(elt)
            if err_code != 0:
                violations[elt] = err_code
            _validate_folder(folder, violations)
        if elt.is_file():
            err_code = _validate_fname(elt)
            if err_code != 0:
                violations[elt] = err_code
    folder_letters = sorted([_parse_folder_name(elt.name)[0][-1] for elt in folders])
    if "".join(folder_letters) != string.ascii_lowercase[: len(folder_letters)]:
        violations[folder] = 200
    return violations


def _validate_folder_name(folder: Path) -> int:
    """Validate a folder name.

    Parameters
    ----------
    folder : Path
        Full path to the folder name to validate.
    context : list of Path
        List of all folders in the same context (parent folder).
    """
    folder_parent_code, _ = _parse_folder_name(folder.parent.name)
    code, name = _parse_folder_name(folder.name)
    if folder_parent_code != code[:-1]:
        return 100
    code_letter = code[-1]
    if code_letter not in string.ascii_lowercase:
        return 101
    if any(elt in name for elt in _FORBIDDEN_STEM_CHARACTERS):
        return 110
    return 0


def _validate_fname(fname: Path) -> int:
    """Validate a file name.

    Parameters
    ----------
    fname : Path
        Full path to the file name to validate.

    Returns
    -------
    error_code : int
        The error code corresponding to the validation error. 0 is returned if no error
        is found.
    """
    folder_code, _ = _parse_folder_name(fname.parent.name)
    try:
        fname_code, date, name, usercode = _parse_file_stem(fname.stem)
    except Exception:
        return 300
    if folder_code != fname_code:
        return 1
    if any(elt in name for elt in _FORBIDDEN_STEM_CHARACTERS):
        return 20
    try:
        date = datetime.strptime(date, "%y%m%d")
    except ValueError:
        return 30
    if datetime.now() < date:
        return 31
    if len(usercode) != _USERCODE_LENGTH:
        return 40
    if any(elt.islower() for elt in usercode):
        return 41
    return 0


def _parse_folder_name(folder: str) -> tuple[str, str]:
    """Parse the folder name."""
    elts = folder.removeprefix("_").split("_")
    code = elts[0]
    name = "_".join(elts[1:])
    return code, name


def _parse_file_stem(stem: str) -> tuple[str, str, str, str]:
    """Parse the file stem."""
    elts = stem.split("_")
    code = elts[0]
    date = elts[1]
    name = "_".join(elts[2:-1])
    usercode = elts[-1]
    return code, date, name, usercode
