_FORBIDDEN_STEM_CHARACTERS: set[str] = {"-", "!", " ", "."}
_USERCODE_LENGTH: int = 3

ERRORS_CODES: dict[int, str] = {
    # file violations
    1: "File code does not match folder code.",
    2: "File name stem contains invalid characters (space, '-', '.', ...).",
    3: "File date format is invalid, expected 'YYMMDD'.",
    4: "File date is in the future.",
    5: f"File user code length is not {_USERCODE_LENGTH} characters.",
    6: "File user code must be uppercase.",
    # folder violations
    100: "Folder code does not match parent folder code.",
    101: "Folder code must end with a lowercase letter.",
    102: "Folder code last letters are not consecutive lowercase letters.",
    103: "Folder name stem contains invalid characters (space, '-', '.', ...).",
    # parser failures
    200: "File name could not be parsed.",
}
