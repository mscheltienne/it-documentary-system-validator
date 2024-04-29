from __future__ import annotations

import random
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from fcbg_ruff.check.validator import validate_folder
from fcbg_ruff.utils._path import walk_files

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(scope="function")
def folder_with_invalid_files(folder: Path) -> tuple[Path, list[Path]]:
    """Create a mock documentary structure with invalid file names."""
    files = [elt for elt in walk_files(folder) if elt.parent.name != "__old"]
    invalid_files = random.sample(files, 4)
    # add a purely invalid fname
    invalid_files[0].rename(invalid_files[0].parent / "invalid_file_name")
    invalid_files[0] = invalid_files[0].parent / "invalid_file_name"
    # add a fname with code not matching parent folder
    fname = invalid_files[1].name.split("_")
    fname[0] += "a"
    fname = "_".join(fname)
    invalid_files[1].rename(invalid_files[1].parent / fname)
    invalid_files[1] = invalid_files[1].parent / fname
    # add a fname with invalid characters in the name
    fname = invalid_files[2].name.split("_")
    fname[2] += " a"
    fname = "_".join(fname)
    invalid_files[2].rename(invalid_files[2].parent / fname)
    invalid_files[2] = invalid_files[2].parent / fname
    # add a fname with a date in the past
    fname = invalid_files[3].name.split("_")
    fname[1] = f"40{fname[1][2:]}"
    fname = "_".join(fname)
    invalid_files[3].rename(invalid_files[3].parent / fname)
    invalid_files[3] = invalid_files[3].parent / fname
    return folder, invalid_files


@pytest.mark.filterwarnings("ignore:The number of requested jobs.*:RuntimeWarning")
@pytest.mark.parametrize("n_jobs", [1, 2])
def test_validate_folder(folder: Path, n_jobs: int):
    """Test validation of a documentary system tree."""
    for elt in folder.iterdir():
        violations = validate_folder(elt, n_jobs=n_jobs)
        assert len(violations["primary"]) == 0
        assert len(violations["secondary"]) == 0


@pytest.mark.filterwarnings("ignore:The number of requested jobs.*:RuntimeWarning")
@pytest.mark.parametrize("n_jobs", [1, 2])
def test_validate_invalid_folder(folder_with_invalid_files: Path, n_jobs: int):
    """Test validation of an invalid documentary system tree."""
    folder, invalid_files = folder_with_invalid_files
    violations = {"primary": dict(), "secondary": dict()}
    for elt in folder.iterdir():
        violations_ = validate_folder(elt, n_jobs=n_jobs)
        for key in ("primary", "secondary"):
            violations[key].update(violations_[key])
    assert len(violations["secondary"]) == 0
    assert violations["primary"][invalid_files[0]] == [1]
    assert violations["primary"][invalid_files[1]] == [11]
    assert violations["primary"][invalid_files[2]] == [3]
    assert violations["primary"][invalid_files[3]] == [21]
