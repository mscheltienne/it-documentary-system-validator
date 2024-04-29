from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from .._regex import (
    PATTERN_FILE_STEM,
    PATTERN_FOLDER_NAME,
    validate_file_name,
    validate_folder_name,
)

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(scope="session")
def valid_file_stem() -> list[str]:
    """Valid file stems."""
    return ["F1_101010_test_ABC", "F2a_101010_test_ABC", "F10abc_101010_test_2_ABC"]


@pytest.fixture(scope="session")
def invalid_file_stem() -> list[str]:
    """Invalid file stems."""
    # do not test with a whitespace 'F1a_101010_test test_ABC', as this is fitlered out
    # by the parser/validator
    return [
        "F1_101010_test_AB1",
        "G2a_101010_test_ABC",
        "F10ab_10101_test_2_ABC",
        "F2",
        "F1a_101010__ABC",
        "F1a_101010___ABC",
    ]


@pytest.fixture(scope="session")
def valid_folder_name() -> list[str]:
    """Valid file stems."""
    return ["_F1_test", "_F2a_test", "_F10abc_test_2"]


@pytest.fixture(scope="session")
def invalid_folder_name() -> list[str]:
    """Invalid file stems."""
    # do not test with a whitespace '_F1a_test ere', as this is fitlered out by the
    # parser/validator
    return ["_G2a_test", "_F10abc", "_F1abc__", "F1_test"]


@pytest.fixture(scope="function")
def valid_fnames(tmp_path: Path, valid_file_stem: list[str]) -> list[Path]:
    """Valid and existing file names."""
    fnames = []
    for stem in valid_file_stem:
        code = stem.split("_")[0]
        (tmp_path / f"_{code}_test").mkdir()
        (tmp_path / f"_{code}_test" / f"{stem}.txt").write_text("101")
        fnames.append(tmp_path / f"_{code}_test" / f"{stem}.txt")
    return fnames


@pytest.fixture(scope="function")
def valid_folders(tmp_path: Path, valid_folder_name: list[str]) -> list[Path]:
    """Valid and existing folder names."""
    folders = []
    for name in valid_folder_name:
        code = name.split("_")[1]
        if code[-1].isnumeric():
            continue
        (tmp_path / f"_{code[:-1]}_test" / name).mkdir(parents=True)
        folders.append(tmp_path / f"_{code[:-1]}_test" / name)
    # add root folders
    for folder in ("_F1_test", "_F10_test_2"):
        (tmp_path / folder).mkdir()
        folders.append(tmp_path / folder)
    return folders


def test_regex_pattern_file_stem(valid_file_stem, invalid_file_stem):
    """Test regex patterns for files."""
    for stem in valid_file_stem:
        assert re.fullmatch(PATTERN_FILE_STEM, stem) is not None
    for stem in invalid_file_stem:
        assert re.fullmatch(PATTERN_FILE_STEM, stem) is None


def test_regex_pattern_folder_name(valid_folder_name, invalid_folder_name):
    """Test regex patterns for folders."""
    for name in valid_folder_name:
        assert re.fullmatch(PATTERN_FOLDER_NAME, name) is not None
    for name in invalid_folder_name:
        assert re.fullmatch(PATTERN_FOLDER_NAME, name) is None


def test_validate_file_name(tmp_path: Path, valid_fnames: list[Path]):
    """Test file name validation."""
    for fname in valid_fnames:
        errors = validate_file_name(fname)
        assert len(errors["primary"]) == 0
        assert len(errors["secondary"]) == 0

    fname = tmp_path / "_F5_test" / "G5_101010_test_ABC.txt"
    fname.parent.mkdir()
    fname.write_text("101")
    errors = validate_file_name(fname)
    assert errors["primary"] == [1]
    assert len(errors["secondary"]) == 0

    fname = tmp_path / "_F5_test" / "F5_101010_test_AB1.txt"
    fname.write_text("101")
    errors = validate_file_name(fname)
    assert errors["primary"] == [1]
    assert len(errors["secondary"]) == 0

    fname = tmp_path / "_F5_test" / "F5_101010_te st_ABC.txt"
    fname.write_text("101")
    errors = validate_file_name(fname)
    assert errors["primary"] == [3]
    assert len(errors["secondary"]) == 0

    fname = tmp_path / "_F1a_test" / "F2a_101010_test_ABC.txt"
    fname.parent.mkdir()
    fname.write_text("101")
    errors = validate_file_name(fname)
    assert errors["primary"] == [11]
    assert len(errors["secondary"]) == 0

    fname = tmp_path / "_F1a_test" / "F1a_401010_test_ABC.txt"
    fname.write_text("101")
    errors = validate_file_name(fname)
    assert errors["primary"] == [21]
    assert len(errors["secondary"]) == 0

    fname = tmp_path / "_test" / "F1a_201010_test_ABC.txt"
    fname.parent.mkdir()
    fname.write_text("101")
    errors = validate_file_name(fname)
    assert len(errors["primary"]) == 0
    assert errors["secondary"] == [101]


def test_validate_folder_name(tmp_path: Path, valid_folders: list[Path]):
    """Test folder name validation."""
    for folder in valid_folders:
        errors = validate_folder_name(folder)
        assert len(errors["primary"]) == 0
        assert len(errors["secondary"]) == 0

    folder = tmp_path / "F5_test"
    folder.mkdir()
    errors = validate_folder_name(folder)
    assert errors["primary"] == [2]
    assert len(errors["secondary"]) == 0

    folder = tmp_path / "_F5_test test"
    folder.mkdir()
    errors = validate_folder_name(folder)
    assert errors["primary"] == [3]
    assert len(errors["secondary"]) == 0

    folder = tmp_path / "_F5_test" / "_F6b_test"
    folder.mkdir(parents=True)
    errors = validate_folder_name(folder)
    assert errors["primary"] == [11]
    assert len(errors["secondary"]) == 0

    folder = tmp_path / "_test" / "_F5b_test"
    folder.mkdir(parents=True)
    errors = validate_folder_name(folder)
    assert len(errors["primary"]) == 0
    assert errors["secondary"] == [101]

    # secondary error is suppressed because F5 corresponds to a root folder.
    folder = tmp_path / "_test" / "_F5_test"
    folder.mkdir(parents=True)
    errors = validate_folder_name(folder)
    assert len(errors["primary"]) == 0
    assert len(errors["secondary"]) == 0
