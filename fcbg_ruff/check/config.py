_FORBIDDEN_NAME_CHARACTERS: set[str] = {"-", "!", " ", "."}
_USERCODE_LENGTH: list[int] = [3]

ERRORS_CODES: dict[int, str] = {
    # pattern violations
    1: "File stem does not match the expected pattern 'CODE_DATE_NAME_USERCODE'.",
    2: "Folder name does not match the expected pattern '_CODE_NAME'.",
    3: "File/Folder name contains invalid characters ('-', '.', spaces, ...).",
    # code violations
    11: "File/Folder code does not match parent folder code.",
    # file-specific violations
    21: "File date is in the future.",
    # secondary violation, depending on a primary violation
    101: "File/Folder code could not be compared to invalid parent pattern.",
}
