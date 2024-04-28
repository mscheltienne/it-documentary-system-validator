from fcbg_ruff.validator._parser import parse_file_stem, parse_folder_name


def test_parse_file_stem():
    """Test parsing of a file stem."""
    code, date, name, usercode = parse_file_stem("F1_210101_name_ABC")
    assert code == "F1"
    assert date == "210101"
    assert name == "name"
    assert usercode == "ABC"

    code, date, name, usercode = parse_file_stem("F1aabc_210101_name_test_ABC")
    assert code == "F1aabc"
    assert date == "210101"
    assert name == "name_test"
    assert usercode == "ABC"


def test_parse_folder_name():
    """Test parsing of a folder name."""
    code, name = parse_folder_name("_F1_name")
    assert code == "F1"
    assert name == "name"

    code, name = parse_folder_name("_F1aabc_name_test")
    assert code == "F1aabc"
    assert name == "name_test"
