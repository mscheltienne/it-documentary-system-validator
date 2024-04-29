from __future__ import annotations

import string
from datetime import datetime
from typing import TYPE_CHECKING

from ._parser import parse_file_stem, parse_folder_name
from .config import _FORBIDDEN_STEM_CHARACTERS, _USERCODE_LENGTH

if TYPE_CHECKING:
    from pathlib import Path


def _validate_root_folder(
    folder: Path,
    primary_violations: dict[Path, list[int]],
    secondary_violations: dict[Path, list[int]],
) -> dict[Path, int]:
    """Validate the content of a folder.

    Parameters
    ----------
    folder : Path
        Full path to the folder to validate.
    %(primary_violations)s
    %(secondary_violations)s

    Returns
    -------
    %(primary_violations)s
    %(secondary_violations)s
    """
    assert folder.is_dir()  # sanity-check
    # validate the current folder name
    errors_folder = _validate_folder_name(folder)
    errors_folder = [err for err in errors_folder if err != 312]
    if len(errors_folder) != 0:
        primary_violations[folder] = errors_folder
    # validate the content of the current folder
    _validate_folder_content(
        folder, errors_folder, primary_violations, secondary_violations
    )


def _validate_non_root_folder(
    folder: Path,
    errors_parent_folder: list[int],
    primary_violations: dict[Path, list[int]],
    secondary_violations: dict[Path, list[int]],
):
    """Validate the content of subfolders recursively."""
    assert folder.is_dir()  # sanity-check
    # validate the current folder name
    errors_folder = _validate_folder_name(folder)
    _triage_primary_and_secondary_violations(
        folder,
        errors_folder,
        errors_parent_folder,
        primary_violations,
        secondary_violations,
    )
    # validate the content of the folder
    _validate_folder_content(
        folder, errors_folder, primary_violations, secondary_violations
    )


def _validate_folder_content(
    folder: Path,
    errors_folder: list[int],
    primary_violations: dict[Path, list[int]],
    secondary_violations: dict[Path, list[int]],
):
    for elt in folder.iterdir():
        if elt.is_dir() and elt.name == "__old":
            pass
        elif elt.is_dir():
            _validate_non_root_folder(
                elt, errors_folder, primary_violations, secondary_violations
            )
        else:  # file
            errors = _validate_fname(elt)
            _triage_primary_and_secondary_violations(
                elt, errors, errors_folder, primary_violations, secondary_violations
            )


def _triage_primary_and_secondary_violations(
    path: Path,
    errors: list[int],
    errors_parent_folder: list[int],
    primary_violations: dict[Path, list[int]],
    secondary_violations: dict[Path, list[int]],
) -> None:
    """Triage primary and secondary violations based on parent folder errors."""
    if len(errors) == 0:
        return
    if len(errors_parent_folder) == 0:
        primary_violations[path] = errors
        return
    # define what is a primary or secondary error
    if any(elt in errors_parent_folder for elt in (101, 102, 103, 104, 105)):
        secondary = {1, 101, 302, 312}
    else:
        secondary = {302, 312}
    # store in the correct variables
    primary_errors = set(errors) - secondary
    secondary_errors = set(errors) & secondary
    if len(primary_errors) != 0:
        primary_violations[path] = list(primary_errors)
    if len(secondary_errors) != 0:
        secondary_violations[path] = list(secondary_errors)


def _validate_folder_name(folder: Path) -> list[int]:
    """Validate a folder name.

    Parameters
    ----------
    folder : Path
        Full path to the folder name to validate.

    Returns
    -------
    error_codes : list of int
        The error code(s) corresponding to the validation error. An empty list is
        returned if no error is found.
    """
    assert folder.is_dir()  # sanity-check
    try:
        code, name = parse_folder_name(folder.name)
    except Exception:
        return [311]
    error_codes = []
    # validate leading underscore and first code letter.
    if not folder.name.startswith("_"):
        error_codes.append(103)
    if folder.name[1] == "_":
        error_codes.append(104)
    if code[0] != "F":
        error_codes.append(105)
    # compare code with parent folder code
    try:
        folder_parent_code, _ = parse_folder_name(folder.parent.name)
        if folder_parent_code != code[:-1]:
            error_codes.append(101)
    except Exception:
        error_codes.append(312)
    # validate that the last code element is a lowercase letter, except for root folders
    if 3 <= len(code):
        code_letter = code[-1]
        if code_letter not in string.ascii_lowercase:
            error_codes.append(102)
    # validate name content
    if any(elt in name for elt in _FORBIDDEN_STEM_CHARACTERS):
        error_codes.append(111)
    return error_codes


def _validate_fname(fname: Path) -> list[int]:
    """Validate a file name.

    Parameters
    ----------
    fname : Path
        Full path to the file name to validate.

    Returns
    -------
    error_codes : list of int
        The error code(s) corresponding to the validation error. An empty list is
        returned if no error is found.
    """
    assert fname.is_file()  # sanity-check
    try:
        fname_code, date, name, usercode = parse_file_stem(fname.stem)
    except Exception:
        return [301]
    error_codes = []
    # compare fname_code with parent folder code
    try:
        folder_code, _ = parse_folder_name(fname.parent.name)
        if folder_code != fname_code:
            error_codes.append(1)
    except Exception:
        error_codes.append(302)
    # validate file code errors
    if 3 <= len(fname_code):
        code_letter = fname_code[-1]
        if code_letter not in string.ascii_lowercase:
            error_codes.append(2)
    if fname.name.startswith("_"):
        error_codes.append(3)
    # validate date format and value
    try:
        date = datetime.strptime(date, "%y%m%d")
        if datetime.now() < date:
            error_codes.append(32)
    except ValueError:
        error_codes.append(31)
    # validate name content
    if any(elt in name for elt in _FORBIDDEN_STEM_CHARACTERS):
        error_codes.append(21)
    # validate usercode
    if len(usercode) != _USERCODE_LENGTH:
        error_codes.append(41)
    if usercode.upper() != usercode:
        error_codes.append(42)
    return error_codes
