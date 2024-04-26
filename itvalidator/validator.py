from __future__ import annotations

from typing import TYPE_CHECKING

from .config import _FORBIDDEN_STEM_CHARACTERS, _USERCODE_LENGTH
from .utils._checks import check_type, ensure_path

if TYPE_CHECKING:
    from pathlib import Path


def validate_folder(folder: str | Path, include_old: bool):
    """Validate the folder and its subfolders.

    Parameters
    ----------
    folder : str | Path
        Folder to validate. The folder and its subfolder will be checked.
    include_old : bool
        If True, the archive '__old' folder will be included in the validation.
    """
    folder = ensure_path(folder, must_exist=True)
    check_type(include_old, (bool,), "include_old")


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
    fname_code, name, usercode = _parse_file_stem(fname.stem)
    if folder_code != fname_code:
        return 1
    if any(elt in name for elt in _FORBIDDEN_STEM_CHARACTERS):
        return 2
    if len(usercode) != _USERCODE_LENGTH:
        return 3
    if any(elt.islower() for elt in usercode):
        return 4
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
