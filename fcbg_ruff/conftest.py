from __future__ import annotations  # c.f. PEP 563, PEP 649

import os
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
    seed = os.environ.get("FCBG_RUFF_RANDOM_SEED", None)
    if seed is not None:
        random.seed(seed)


@pytest.fixture(scope="function")
def folder(tmp_path: Path) -> Path:
    """Create a mock documentary structure."""
    for code in "F1", "F2", "F3":
        curdir = tmp_path / f"_{code}_{_random_name()}"
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
        curdir = folder / f"_{code_subfolder}_{_random_name()}"
        curdir.mkdir()
        _create_tree(curdir, code_subfolder, depth + 1)


def _create_files(folder: Path, code: str) -> None:
    """Create random files in the folder and in '__Old'."""
    n_files = random.randint(0, 4)
    if n_files == 0:
        return
    old = random.choice([True, True, False])  # include old folder
    for _ in range(n_files + 1):
        fname = _random_fname_stem(code)
        (folder / fname).with_suffix(".txt").write_text("101")
        if old and random.choice([True, True, False]):
            fname = _olderify_fname(fname)
            fname = _change_fname_usercode(fname)
            (folder / "__Old").mkdir(exist_ok=True)
            (folder / "__Old" / fname).with_suffix(".txt").write_text("101")


def _random_name() -> str:
    """Create a random file/folder name."""
    segments = random.randint(1, 3)
    return "_".join(str(uuid4()).split("-")[:segments])


def _random_fname_stem(code: str) -> str:
    """Create a random file name stem."""
    year = random.randint(19, 23)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    datecode = f"{year:02d}{month:02d}{day:02d}"
    name = _random_name()
    usercode = "".join(random.sample(string.ascii_lowercase, 3)).upper()
    return f"{code}_{datecode}_{name}_{usercode}"


def _olderify_fname(fname: str) -> str:
    """Change the date in the file name."""
    fname = fname.split("_")
    date = datetime.strptime(fname[1], "%y%m%d")
    date -= timedelta(days=random.randint(1, 700))
    fname[1] = date.strftime("%y%m%d")
    return "_".join(fname)


def _change_fname_usercode(fname: str) -> str:
    """Randomly change the user code in the file name."""
    if random.choice([True, False]):
        return fname
    fname = fname.split("_")
    fname[-1] = "".join(random.sample(string.ascii_lowercase, 3)).upper()
    return "_".join(fname)
