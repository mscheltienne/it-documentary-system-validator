from __future__ import annotations

import re
from datetime import datetime
from typing import TYPE_CHECKING

from ..utils.logs import logger, warn
from ._parser import parse_file_stem, parse_folder_name
from .config import _FORBIDDEN_NAME_CHARACTERS, _USERCODE_LENGTH

if TYPE_CHECKING:
    from pathib import Path


PATTERN_USERCODE_STR: str = f"[A-Z]{','.join([str(i) for i in _USERCODE_LENGTH])}"
PATTERN_FILE_STEM = re.compile(r"F\d+[a-z]*_\d{6}_.*_" + PATTERN_USERCODE_STR)
PATTERN_FOLDER_NAME = re.compile(r"_F\d+[a-z]*_.*")


def validate_file_name(fname: Path) -> dict[str, list[int]]:
    """Validate a file name.

    Parameters
    ----------
    fname : Path
        Full path to the file name to validate.

    Returns
    -------
    error_codes : dict
        Dictionary of error codes, separated between primary and secondary errors.
    """
    assert fname.is_file()  # sanity-check
    match = re.fullmatch(PATTERN_FILE_STEM, fname.stem)
    if match is None:
        return {"primary": [1]}
    # parse the file name and validate its content based on context
    try:
        fname_code, date, name, _ = parse_file_stem(fname.stem)
    except Exception as error:  # should never happen
        warn(
            f"File name stem '{fname.stem}' could not be parsed. Please report this "
            "warning on the issue tracker."
        )
        logger.exception(error)
    error_codes = dict(primary=[], secondary=[])
    _validate_file_name_code(fname_code, fname, error_codes)
    _validate_file_name_date(date, fname, error_codes)
    _validate_name_content(name, fname, error_codes)
    return error_codes


def _validate_file_name_code(
    fname_code: str, fname: Path, error_codes: dict[str, list[int]]
) -> None:
    """Validate the code in a file name."""
    match = re.fullmatch(PATTERN_FOLDER_NAME, fname.parent.name)
    if match is None:
        error_codes["secondary"].append(101)
        return
    try:
        folder_code, _ = parse_folder_name(fname.parent.name)
        if folder_code != fname_code:
            error_codes["primary"].append(11)
    except Exception as error:
        warn(
            f"Folder name '{fname.parent.name}' could not be parsed. Please report "
            "this warning on the issue tracker."
        )
        logger.exception(error)


def _validate_file_name_date(
    date: str, fname: Path, error_codes: dict[str, list[int]]
) -> None:
    """Validate the date in a file name."""
    try:
        date = datetime.strptime(date, "%y%m%d")
        if datetime.now() < date:
            error_codes["primary"].append(21)
    except Exception as error:
        warn(
            f"Date '{date}' in file name '{fname.name}' could not be parsed. Please "
            "report this warning on the issue tracker."
        )
        logger.exception(error)


def _validate_name_content(
    name: str, path: Path, error_codes: dict[str, list[int]]
) -> None:
    """Validate the file name content."""
    if len(name) == 0:
        warn(
            f"The {'file' if path.is_file() else 'folder'} name '{path.name}' has an "
            "empty parsed 'name' field. Please report this warning on the issue "
            "tracker."
        )
        return
    if any(elt in name for elt in _FORBIDDEN_NAME_CHARACTERS):
        error_codes["primary"].append(3)


def validate_folder_name(folder: Path) -> dict[str, list[int]]:
    """Validate a folder name.

    Parameters
    ----------
    folder : Path
        Full path to the folder name to validate.
    """
    assert folder.is_dir()  # sanity-check
    match = re.fullmatch(PATTERN_FOLDER_NAME, folder.name)
    if match is None:
        return {"primary": [2]}
    # parse the folder name and validate its content based on context
    try:
        folder_code, name = parse_folder_name(folder.name)
    except Exception as error:  # should never happen
        warn(
            f"Folder name '{folder.name}' could not be parsed. Please report this "
            "warning on the issue tracker."
        )
        logger.exception(error)
    error_codes = dict(primary=[], secondary=[])
    _validate_folder_name_code(folder_code, folder, error_codes)
    _validate_name_content(name, folder, error_codes)
    return error_codes


def _validate_folder_name_code(
    folder_code: str, folder: Path, error_codes: dict[str, list[int]]
) -> None:
    """Validate the code in a folder name."""
    if folder.parent is None:  # we might be at the root of a file system
        return
    match = re.fullmatch(PATTERN_FOLDER_NAME, folder.parent.name)
    # check folder code against parent folder code
    if match is None:
        pattern = re.compile(r"F\d+([a-z]*)")  # select letters from the folder code
        letters = re.fullmatch(pattern, folder.name).group(1)
        if len(letters) != 0:
            error_codes["secondary"].append(101)
        return
    try:
        parent_folder_code, _ = parse_folder_name(folder.parent.name)
        if parent_folder_code != folder_code[:-1]:
            error_codes["primary"].append(11)
    except Exception as error:
        warn(
            f"Folder name '{folder.parent.name}' could not be parsed. Please report "
            "this warning on the issue tracker."
        )
        logger.exception(error)
