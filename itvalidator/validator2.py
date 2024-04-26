from __future__ import annotations

import string
from datetime import datetime
from typing import TYPE_CHECKING

from ._parser import parse_file_stem, parse_folder_name
from .config import _FORBIDDEN_STEM_CHARACTERS, _USERCODE_LENGTH

if TYPE_CHECKING:
    from pathlib import Path


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
        return [310]
    error_codes = []
    # validate leading underscore and first code letter.
    if not folder.name.startswith("_"):
        error_codes.append(102)
    if folder.name[1] == "_":
        error_codes.append(103)
    if code[0] != "F":
        error_codes.append(104)
    # compare code with parent folder code
    try:
        folder_parent_code, _ = parse_folder_name(folder.parent.name)
        if folder_parent_code != code[:-1]:
            error_codes.append(100)
    except Exception:
        error_codes.append(311)
    # validate that the last code element is a lowercase letter, except for root folders
    if 3 <= len(code):
        code_letter = code[-1]
        if code_letter not in string.ascii_lowercase:
            error_codes.append(101)
    # validate name content
    if any(elt in name for elt in _FORBIDDEN_STEM_CHARACTERS):
        error_codes.append(110)
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
        return [300]
    error_codes = []
    # compare fname_code with parent folder code
    try:
        folder_code, _ = parse_folder_name(fname.parent.name)
        if folder_code != fname_code:
            error_codes.append(1)
    except Exception:
        error_codes.append(301)
    # validate date format and value
    try:
        date = datetime.strptime(date, "%y%m%d")
        if datetime.now() < date:
            error_codes.append(31)
    except ValueError:
        error_codes.append(30)
    # validate name content
    if any(elt in name for elt in _FORBIDDEN_STEM_CHARACTERS):
        error_codes.append(20)
    # validate usercode
    if len(usercode) != _USERCODE_LENGTH:
        error_codes.append(40)
    if usercode.upper() != usercode:
        error_codes.append(41)
    return error_codes
