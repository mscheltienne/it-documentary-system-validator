from __future__ import annotations  # c.f. PEP 563 and PEP 649

import random
from shutil import move
from typing import TYPE_CHECKING

import pytest
from fcbg_ruff.validator import _parse_file_stem, _parse_folder_name, validate_folder

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


def _walk_files(path: Path) -> Generator[Path, None, None]:
    """Walk recursively through a directory tree and yield the existing files.

    Parameters
    ----------
    path : Path
        Path to a directory.
    """
    if not path.is_dir():
        raise RuntimeError(
            f"The provided path '{path}' is not a directory. It can not be walked."
        )
    for entry in path.iterdir():
        if entry.is_dir():
            yield from _walk_files(entry)
        else:
            yield entry


def _walk_folders(path: Path) -> Generator[Path, None, None]:
    """Walk recursively through a directory tree and yield the existing folders.

    Parameters
    ----------
    path : Path
        Path to a directory.
    """
    if not path.is_dir():
        raise RuntimeError(
            f"The provided path '{path}' is not a directory. It can not be walked."
        )
    for entry in path.iterdir():
        if entry.is_dir():
            yield from _walk_folders(entry)
            yield entry


@pytest.mark.parametrize("n_jobs", [1, 2])
@pytest.mark.filterwarnings("ignore:The number of requested jobs.*:RuntimeWarning")
def test_validator(folder, n_jobs):
    """Test validation of a folder."""
    for folder_ in folder.iterdir():
        violations = validate_folder(folder_, n_jobs=n_jobs)
        assert len(violations) == 0


@pytest.mark.parametrize("n_jobs", [1, 2])
@pytest.mark.filterwarnings("ignore:The number of requested jobs.*:RuntimeWarning")
def test_validator_filecode(folder, n_jobs):
    """Test validation of paths with wrong file codes."""
    files = list(_walk_files(folder))
    files = random.sample(files, min(4, len(files)))
    new_files = []
    for file in files:
        code, date, name, usercode = _parse_file_stem(file.stem)
        code = f"{code}1"
        new_file = file.with_name(f"{code}_{date}_{name}_{usercode}{file.suffix}")
        move(file, new_file)
        new_files.append(new_file)

    all_violations = dict()
    for folder_ in folder.iterdir():
        violations = validate_folder(folder_, n_jobs=n_jobs)
        assert all(elt in new_files for elt in violations)
        assert all(err_code == 1 for err_code in violations.values())
        all_violations.update(violations)
    assert all(elt in new_files for elt in all_violations)
    assert all(err_code == 1 for err_code in all_violations.values())


@pytest.mark.parametrize("n_jobs", [1, 2])
@pytest.mark.filterwarnings("ignore:The number of requested jobs.*:RuntimeWarning")
def test_validator_folder_code(folder, n_jobs):
    """Test validation of paths with wrong folder codes."""
    folders = [elt for elt in _walk_folders(folder) if elt.name != "__old"]
    folders = random.sample(folders, min(4, len(folders)))
    new_folders = []
    for fold in folders:
        code, name = _parse_folder_name(fold.name)
        code = f"{code}dsd"
        new_folder = fold.with_name(f"_{code}_{name}")
        move(fold, new_folder)
        new_folders.append(new_folder)

    # check for violation without parallel processing
    all_violations = dict()
    for folder_ in folder.iterdir():
        violations = validate_folder(folder_, n_jobs=n_jobs)
        assert all(elt in new_folders for elt in violations)
        assert all(err_code == 1 for err_code in violations.values())
        all_violations.update(violations)
    assert all(elt in new_folders for elt in all_violations)
    assert all(err_code == 1 for err_code in all_violations.values())
