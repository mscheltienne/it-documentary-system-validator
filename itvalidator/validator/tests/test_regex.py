import re

import pytest

from .._regex import PATTERN_FILE_STEM, PATTERN_FOLDER_NAME


@pytest.scope("session")
def valid_file_stem() -> list[str]:
    """Valid file stems."""
    return ["F1_101010_test_ABC", "F2a_101010_test_ABC", "F10abc_101010_test_2_ABC"]


@pytest.scope("session")
def invalid_file_stem() -> list[str]:
    """Invalid file stems."""
    return [
        "F1_101010_test_AB1",
        "G2a_101010_test_ABC",
        "F10ab_10101_test_2_ABC",
        "F2",
        "F1a_101010__ABC",
    ]


@pytest.scope("session")
def valid_folder_name() -> list[str]:
    """Valid file stems."""
    return ["F1_test", "F2a_test", "F10abc_test_2"]


@pytest.scope("session")
def invalid_folder_name() -> list[str]:
    """Invalid file stems."""
    return ["F1_101010_test_AB1", "G2a_test", "F10abc", "F1abc__"]


def test_regex_pattern_file_stem(valid_file_stem, invalid_file_stem):
    """Test regex patterns for files."""
    for stem in valid_file_stem:
        assert re.fullmatch(PATTERN_FILE_STEM, stem) is not None
    for stem in invalid_file_stem:
        assert re.fullmatch(PATTERN_FILE_STEM, stem) is None


def test_regex_pattern_folder_name(valid_folder_name, invalid_folder_name):
    """Test regex patterns for folders."""
    for stem in valid_folder_name:
        assert re.fullmatch(PATTERN_FILE_STEM, stem) is not None
    for stem in invalid_folder_name:
        assert re.fullmatch(PATTERN_FOLDER_NAME, stem) is None
