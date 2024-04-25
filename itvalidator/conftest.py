from __future__ import annotations  # c.f. PEP 563, PEP 649

import random
import string
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from .utils.logs import logger

if TYPE_CHECKING:
    from pathlib import Path

    from pytest import Config


_MAX_TREE_DEPTH: int = 4


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
        segments = random.randint(1, 3)
        name = "_".join(str(uuid4()).split("-")[:segments])
        curdir = tmp_path / f"_{code}_{name}"
        curdir.mkdir()
        _create_tree(curdir, code, depth=1)
    return tmp_path


def _random_datecode(datelimit: str | None = None) -> str:
    """Create a random datecode"""
    if datelimit is None:
        year = random.randint(19, 25)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        date = f"{year:02d}{month:02d}{day:02d}"
    else:
        datelimit = datetime.strptime(datelimit, "%y%m%d")
        date = datelimit - timedelta(days=random.randint(1, 700))
        date = date.strftime("%y%m%d")
    return date


def _random_name(code: str) -> str:
    """Create a random file/folder name."""
    datecode = _random_datecode()
    segments = random.randint(1, 3)
    name = "_".join(str(uuid4()).split("-")[:segments])
    usercode = "".join(random.sample(string.ascii_lowercase, 3)).upper()
    return f"_{code}_{datecode}_{name}_{usercode}"


def _create_files(folder: Path, code: str):
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


def _create_tree(folder: Path, code: str, depth: int):
    """Create a directory tree."""
    _create_files(folder, code)
    if depth == _MAX_TREE_DEPTH:
        return
    n_subfolders = random.randint(0, 3)
    for k in range(n_subfolders + 1):
        code_subfolder = f"{code}{string.ascii_lowercase[k]}"
        curdir = folder / _random_name(code_subfolder)
        curdir.mkdir()
        _create_tree(curdir, code_subfolder, depth + 1)
