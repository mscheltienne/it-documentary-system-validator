from itvalidator.validator import validate_folder


def test_validator(folder):
    """Test validation of a folder."""
    for folder_ in folder.iterdir():
        violations = validate_folder(folder_)
        assert len(violations) == 0
