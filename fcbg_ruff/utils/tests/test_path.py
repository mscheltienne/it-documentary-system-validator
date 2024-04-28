import pytest
from fcbg_ruff.utils._path import walk_files, walk_folders


def test_walk_files(tmp_path):
    """Test walk_files generator."""
    fname1 = tmp_path / "file1"
    fname1.write_text("101")
    fname2 = tmp_path / "file2"
    fname2.write_text("101")
    (tmp_path / "dir1" / "dir2").mkdir(parents=True)
    fname3 = tmp_path / "dir1" / "file3"
    fname3.write_text("101")
    fname4 = tmp_path / "dir1" / "dir2" / "file1"
    fname4.write_text("101")
    files = list(walk_files(tmp_path))
    assert all(fname in files for fname in (fname1, fname2, fname3, fname4))
    with pytest.raises(RuntimeError, match="not a directory"):
        list(walk_files(fname1))


def test_walk_folders(tmp_path):
    """Test walk_folders generator."""
    (tmp_path / "file1").write_text("101")
    folder1 = tmp_path / "dir1"
    folder1.mkdir()
    folder2 = tmp_path / "dir1" / "dir2"
    folder2.mkdir()
    folder3 = tmp_path / "dir1" / "dir3"
    folder3.mkdir()
    folders = list(walk_folders(tmp_path))
    assert all(folder in folders for folder in (folder1, folder2, folder3))
    with pytest.raises(RuntimeError, match="not a directory"):
        list(walk_folders(tmp_path / "file1"))
