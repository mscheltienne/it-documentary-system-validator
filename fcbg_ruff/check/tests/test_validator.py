from fcbg_ruff.check.validator import validate_folder


def test_validate_folder(folder):
    """Test validation of a documentary system tree."""
    for elt in folder.iterdir():
        violations = validate_folder(elt)
        assert len(violations["primary"]) == 0
        assert len(violations["secondary"]) == 0
