from __future__ import annotations

import multiprocessing as mp
import string
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from .config import _FORBIDDEN_STEM_CHARACTERS, _USERCODE_LENGTH
from .utils._checks import ensure_int, ensure_path
from .utils.logs import warn

if TYPE_CHECKING:
    from pathlib import Path


def validate_folder(folder: Path | str, n_jobs: int = 1) -> dict[Path, int]:
    """Validate a folder and its content.

    Parameters
    ----------
    folder : Path | str
        Path to the folder to validate. The folder name should respect the documentary
        system naming schema. Thus, it can not be called on the root of the documentary
        system share.
    n_jobs : int
        Number of concurrent workers used for validation. The subfolders are split
        between workers, thus the most workers you can have is defined by the number of
        subfolders in the folder.

    Returns
    -------
    violations : dict
        Dictionary of violations found in the folder and its content.
    """
    folder = ensure_path(folder, must_exist=True)
    n_jobs = ensure_int(n_jobs)
    if n_jobs < 1:
        raise ValueError("The number of jobs must be an integer greater or equal to 1.")
    # validate folder name and file content
    err_code = _validate_folder_name(folder, validate_parent_code=False)
    violations = {folder: err_code} if err_code != 0 else dict()
    for elt in folder.iterdir():
        if elt.is_dir():
            continue
        err_code = _validate_fname(elt)
        if err_code != 0:
            violations[elt] = err_code
    # validate subfolders and subfolders content
    if n_jobs == 1:
        violations = _validate_folder_content(folder, violations)
    else:
        folders = [
            elt for elt in folder.iterdir() if elt.is_dir() and elt.name != "__old"
        ]
        if len(folders) < n_jobs:
            warn(
                f"The number of requested jobs {n_jobs} is greater than the number of "
                f"subfolders {len(folders)}. The number of jobs will be reduced to "
                f"{len(folders)}."
            )
            n_jobs = len(folders)
        if mp.cpu_count() < n_jobs:
            warn(
                f"The number of requested jobs {n_jobs} is greater than the number of "
                f"available CPUs {mp.cpu_count()}. The number of jobs will be reduced "
                f"to {mp.cpu_count()}."
            )
            n_jobs = mp.cpu_count()
        with mp.Pool(processes=n_jobs, maxtasksperchild=1) as pool:
            results = pool.starmap(
                _validate_folder_content, [(folder, dict()) for folder in folders]
            )
        for result in results:
            violations.update(result)
    return violations


def _validate_folder_content(
    folder: Path, violations: dict[Path, int]
) -> dict[Path, int]:
    """Validate the content of a folder.

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
    folders = []  # list folders to validate last code letter consecutiveness
    for elt in folder.iterdir():
        if elt.is_dir() and elt.name != "__old":
            folders.append(elt)
            err_code = _validate_folder_name(elt)
            if err_code != 0:
                violations[elt] = err_code
            _validate_folder_content(elt, violations)
        if elt.is_file():
            err_code = _validate_fname(elt)
            if err_code != 0:
                violations[elt] = err_code
    try:
        folder_letters = sorted(
            [_parse_folder_name(elt.name)[0][-1] for elt in folders]
        )
        if "".join(folder_letters) != string.ascii_lowercase[: len(folder_letters)]:
            violations[folder] = 200
    except Exception:
        violations[folder] = 320
    return violations


def _validate_folder_name(folder: Path, validate_parent_code: bool = True) -> int:
    """Validate a folder name.

    Parameters
    ----------
    folder : Path
        Full path to the folder name to validate.
    validate_parent_code : bool
        If False, ignore the code validation based on the parent folder.
    """
    if not folder.name.startswith("_"):
        return 102
    try:
        code, name = _parse_folder_name(folder.name)
    except Exception:
        return 310
    if code[0] != "F":
        return 103
    if validate_parent_code:
        try:
            folder_parent_code, _ = _parse_folder_name(folder.parent.name)
        except Exception:
            return 311
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
    try:
        folder_code, _ = _parse_folder_name(fname.parent.name)
    except Exception:
        return 301
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
