from __future__ import annotations

from typing import TYPE_CHECKING

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
