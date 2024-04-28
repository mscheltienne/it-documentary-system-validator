from __future__ import annotations

from re import compile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from re import Pattern

_PATTERN_CODE_NUM: Pattern = compile(r"F\d+")


def _validate_code(code: str) -> list[int]:
    """Validate a file or folder code."""
    error_codes = []
    if code[0] != "F":
        error_codes.append(105)
    match = re.match(PATTERN_CODE_NUM, code)
    if match is None:
        pass
    match.group()
