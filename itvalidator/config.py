_FORBIDDEN_STEM_CHARACTERS: set[str] = {"-", "!", " ", "."}
_USERCODE_LENGTH: int = 3

ERRORS_CODES: dict[int, str] = {
    # file violations
    1: "File code does not match folder code.",
    20: "File name stem contains invalid characters (space, '-', '.', ...).",
    30: "File date format is invalid, expected 'YYMMDD'.",
    31: "File date is in the future.",
    40: f"File user code length is not {_USERCODE_LENGTH} characters.",
    41: "File user code must be uppercase.",
    # folder violations
    100: "Folder code does not match parent folder code.",
    101: "Folder code must end with a lowercase letter, except root folders.",
    102: "Folder code must start with a leading underscore.",
    103: "Folder code has multiple leading underscores.",
    104: "Folder code must start with 'F'.",
    110: "Folder name stem contains invalid characters (space, '-', '.', ...).",
    # subfolder violations
    200: "Subfolders code last letters are not consecutive lowercase letters.",
    # parser failures
    300: "File name could not be parsed.",
    301: "File name could not be validated because parent folder is invalid.",
    310: "Folder name could not be parsed.",
    311: "Folder name could not be validated because parent folder is invalid.",
    320: "Subfolders code last letters could not be validated because at least one subfolder is invalid.",  # noqa: E501
}
