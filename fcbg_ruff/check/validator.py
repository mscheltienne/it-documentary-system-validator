from __future__ import annotations

import multiprocessing as mp
from typing import TYPE_CHECKING

from ..utils._checks import ensure_int, ensure_path
from ..utils._docs import fill_doc
from ..utils.logs import warn
from ._regex import validate_file_name, validate_folder_name

if TYPE_CHECKING:
    from pathlib import Path


@fill_doc
def validate_folder(
    folder: Path | str, n_jobs: int = 1
) -> dict[str, dict[Path, list[int]]]:
    """Validate a folder from the documentary system and its content recursively.

    Parameters
    ----------
    folder : Path | str
        Path to the folder to validate.
    n_jobs : int
        Number of concurrent workers used for validation. The subfolders are split
        between workers, thus the most workers you can have is defined by the number of
        subfolders in 'folder'.

    Returns
    -------
    %(violations)s
    """
    folder = ensure_path(folder, must_exist=True)
    n_jobs = ensure_int(n_jobs)
    violations = {"primary": dict(), "secondary": dict()}
    if n_jobs == 1:
        _validate_folder(folder, violations)
    else:
        folders = []  # list subfolders and validate files
        for elt in folder.iterdir():
            if elt.is_file():
                errors = validate_file_name(elt)
                for key in ("primary", "secondary"):
                    if len(errors[key]) != 0:
                        violations[key][elt] = errors[key]
            elif elt.is_dir() and elt.name != "__old":
                folders.append(elt)
        # validate subfolders in parallel
        n_jobs = _ensure_n_jobs(n_jobs, len(folders))
        with mp.Pool(processes=n_jobs, maxtasksperchild=1) as pool:
            results = pool.starmap(validate_folder, [(folder, 1) for folder in folders])
        for result in results:
            for key in ("primary", "secondary"):
                violations[key].update(result[key])
    return violations


@fill_doc
def _validate_folder(
    folder: Path, violations: dict[str, dict[Path, list[int]]]
) -> None:
    """Validate a folder and its content recursively.

    Parameters
    ----------
    folder : Path
        Path to the folder to validate.
    %(violations)s
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


def _ensure_n_jobs(n_jobs: int, n_folders: int) -> int:
    """Ensure the n_jobs argument value is valid."""
    if n_jobs < 1:
        raise ValueError("The number of jobs must be an integer greater or equal to 1.")
    if n_folders < n_jobs:
        warn(
            f"The number of requested jobs {n_jobs} is greater than the number of "
            f"subfolders {n_folders}. The number of jobs will be reduced to "
            f"{n_folders}."
        )
        n_jobs = n_folders
    if mp.cpu_count() < n_jobs:
        warn(
            f"The number of requested jobs {n_jobs} is greater than the number of "
            f"available CPUs {mp.cpu_count()}. The number of jobs will be reduced "
            f"to {mp.cpu_count()}."
        )
        n_jobs = mp.cpu_count()
    return n_jobs
