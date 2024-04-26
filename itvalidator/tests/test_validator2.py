from datetime import datetime

from itvalidator.validator2 import _validate_fname, _validate_folder_name


def test_validate_fname(tmp_path):
    """Test validation of a file name."""
    (tmp_path / "_F1_folder").mkdir()
    fname = tmp_path / "_F1_folder" / "F1_220101_file_ABC.txt"
    fname.write_text("101")
    err = _validate_fname(fname)
    assert len(err) == 0

    # unparseable
    fname = tmp_path / "_F1_folder" / "test.txt"
    fname.write_text("101")
    err = _validate_fname(fname)
    assert err == [300]

    (tmp_path / "_F1folder").mkdir()
    fname = tmp_path / "_F1folder" / "F1_220101_file_ABC.txt"
    fname.write_text("101")
    err = _validate_fname(fname)
    assert err == [301]

    # invalid file names
    fname = tmp_path / "_F1_folder" / "F1a_2201_file-test_ABCD.txt"
    fname.write_text("101")
    err = _validate_fname(fname)
    assert sorted(err) == [1, 20, 30, 40]

    fname = tmp_path / "_F1_folder" / "F1_400101_file_test_ABc.txt"
    fname.write_text("101")
    err = _validate_fname(fname)
    expected = (
        [31, 41] if datetime.now() < datetime(year=2040, month=1, day=1) else [41]
    )
    assert sorted(err) == expected


def test_validate_folder_name(tmp_path):
    """Test validation of a folder name."""
    folder = tmp_path / "_F1_folder" / "_F1a_subfolder"
    folder.mkdir(parents=True)
    err = _validate_folder_name(folder)
    assert len(err) == 0

    # unparseable
    folder = tmp_path / "_F1_folder" / "_F1asubfolder"
    folder.mkdir(parents=True)
    err = _validate_folder_name(folder)
    assert err == [310]

    folder = tmp_path / "_F1_folder" / "test"
    folder.mkdir(parents=True)
    err = _validate_folder_name(folder)
    assert err == [310]

    folder = tmp_path / "_F1folder" / "_F1a_subfolder"
    folder.mkdir(parents=True)
    err = _validate_folder_name(folder)
    assert err == [311]

    # invalid folder names
    folder = tmp_path / "_F1_folder" / "G1A_subfolder-test"
    folder.mkdir(parents=True)
    err = _validate_folder_name(folder)
    assert sorted(err) == [100, 101, 102, 104, 110]

    folder = tmp_path / "_F1_folder" / "__F1a_subfolder"
    folder.mkdir(parents=True)
    err = _validate_folder_name(folder)
    assert err == [103]
