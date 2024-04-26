import pytest

from itvalidator._parser import parse_file_stem, parse_folder_name


def test_parse_file_stem():
    """Test parsing of a file stem."""
    fname = "F1_210101_name_ABC"
    code, date, name, usercode = parse_file_stem(fname)
    assert code == "F1"
    assert date == "210101"
    assert name == "name"
    assert usercode == "ABC"

    fname = "F1aabc_210101_name_test_ABC"
    code, date, name, usercode = parse_file_stem(fname)
    assert code == "F1aabc"
    assert date == "210101"
    assert name == "name_test"
    assert usercode == "ABC"

    fname = "_F1aa_210101_name_test_ABC"
    code, date, name, usercode = parse_file_stem(fname)
    assert code == "F1aa"
    assert date == "210101"
    assert name == "name_test"
    assert usercode == "ABC"


def test_parse_folder_name():
    """Test parsing of a folder name."""
    folder = "_F1_name"
    code, name = parse_folder_name(folder)
    assert code == "F1"
    assert name == "name"

    folder = "_F1aabc_name_test"
    code, name = parse_folder_name(folder)
    assert code == "F1aabc"
    assert name == "name_test"


def test_parse_invalid_folder_name():
    """Test parsing of an invalid folder name."""
    folder = "_F1ererwr"
    with pytest.raises(RuntimeError, match="Folder name could not be parsed."):
        parse_folder_name(folder)
