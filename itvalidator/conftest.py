from __future__ import annotations  # c.f. PEP 563, PEP 649

import random
import string
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from .utils.logs import logger

if TYPE_CHECKING:
    from pathlib import Path

    from pytest import Config


_MAX_TEST_TREE_DEPTH: int = 4


def pytest_configure(config: Config) -> None:
    """Configure pytest options."""
    warnings_lines = r"""
    error::
    """
    for warning_line in warnings_lines.split("\n"):
        warning_line = warning_line.strip()
        if warning_line and not warning_line.startswith("#"):
            config.addinivalue_line("filterwarnings", warning_line)
    # setup logging
    logger.propagate = True
    # set random seed
    random.seed(101)


@pytest.fixture(scope="session")
def folder(tmp_path: Path) -> Path:
    """Create a mock documentary structure."""
    for code in "F1", "F2", "F3":
        curdir = tmp_path / f"_{code}_{_random_stem()}"
        curdir.mkdir()
        _create_tree(curdir, code, depth=1)
    return tmp_path


def _create_tree(folder: Path, code: str, depth: int) -> None:
    """Create a directory tree."""
    _create_files(folder, code)
    if depth == _MAX_TEST_TREE_DEPTH:
        return
    n_subfolders = random.randint(0, 3)
    for k in range(n_subfolders + 1):
        code_subfolder = f"{code}{string.ascii_lowercase[k]}"
        curdir = folder / f"_{code_subfolder}_{_random_stem()}"
        curdir.mkdir()
        _create_tree(curdir, code_subfolder, depth + 1)


def _create_files(folder: Path, code: str) -> None:
    """Create random files in the folder and in '__old'."""
    n_files = random.randint(0, 4)
    if n_files == 0:
        return
    old = random.choice([True, True, False])  # include old folder
    for _ in range(n_files + 1):
        fname = _random_name(code)
        (folder / fname).with_suffix(".txt").write_text("101")
        if old and random.choice([True, True, False]):
            (folder / "__old").mkdir(exist_ok=True)
            (folder / "__old" / fname).with_suffix(".txt").write_text("101")


def _random_stem() -> str:
    """Create a random file/folder stem."""
    segments = random.randint(1, 3)
    return "_".join(str(uuid4()).split("-")[:segments])


def _random_name(code: str) -> str:
    """Create a random file name."""
    year = random.randint(19, 25)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    datecode = f"{year:02d}{month:02d}{day:02d}"
    name = _random_stem()
    usercode = "".join(random.sample(string.ascii_lowercase, 3)).upper()
    return f"{code}_{datecode}_{name}_{usercode}"
