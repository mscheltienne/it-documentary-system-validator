import random
from pathlib import Path

import pytest
from click.testing import CliRunner

from ...utils._path import walk_files
from ..check import run


def test_check(folder: Path, tmp_path: Path):
    """Test the check command."""
    runner = CliRunner()
    for elt in folder.iterdir():
        if elt.is_file():
            continue
        output = tmp_path / f"{elt.stem}.txt"
        result = runner.invoke(run, [str(elt), "--output", str(output)])
        assert result.exit_code == 0
        with open(output) as fid:
            lines = fid.readlines()
        # with the spacing used, that corresponds to 0 violations
        assert "Primary violations:" in lines[1]
        assert "Secondary violations:" in lines[4]


@pytest.fixture(scope="function")
def folder_with_invalid_files(folder: Path) -> Path:
    """Create a mock documentary structure with invalid file names."""
    files = [elt for elt in walk_files(folder) if elt.parent.name.lower() != "__old"]
    invalid_files = random.sample(files, 2)
    invalid_files[0].rename(invalid_files[0].parent / ".DS_Store")
    invalid_files[1].rename(invalid_files[1].parent / ".Thumbs")
    return folder


def test_check_ignore(folder_with_invalid_files: Path, tmp_path):
    """Test the check command with ignored patterns."""
    runner = CliRunner()
    for elt in folder_with_invalid_files.iterdir():
        if elt.is_file():
            continue
        output = tmp_path / f"{elt.stem}.txt"
        result = runner.invoke(
            run,
            [str(elt), "--output", str(output), "-i", "*/.DS_Store", "-i", "*/.Thumbs"],
        )
        assert result.exit_code == 0
        with open(output) as fid:
            lines = fid.readlines()
        # with the spacing used, that corresponds to 0 violations
        assert "Primary violations:" in lines[1]
        assert "Secondary violations:" in lines[4]

    outputs = []
    for elt in folder_with_invalid_files.iterdir():
        if elt.is_file():
            continue
        output = tmp_path / f"{elt.stem}.txt"
        result = runner.invoke(
            run,
            [str(elt), "--output", str(output), "-i", "*/.Thumbs"],
        )
        assert result.exit_code == 0
        with open(output) as fid:
            outputs.extend(fid.readlines())
    assert any(".DS_Store" in elt for elt in outputs)
    assert not any(".Thumbs" in elt for elt in outputs)
