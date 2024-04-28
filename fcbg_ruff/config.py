_FORBIDDEN_STEM_CHARACTERS: set[str] = {"-", "!", " ", "."}
_USERCODE_LENGTH: int = 3

ERRORS_CODES: dict[int, str] = {
    # file violations
    1: "File code does not match folder code.",
    2: "File code must end with a lowercase letter, except for root folders.",
    3: "File code must not start with a leading underscore.",
    21: "File name stem contains invalid characters (space, '-', '.', ...).",
    31: "File date format is invalid, expected 'YYMMDD'.",
    32: "File date is in the future.",
    41: f"File user code length is not {_USERCODE_LENGTH} characters.",
    42: "File user code must be uppercase.",
    # folder violations
    101: "Folder code does not match parent folder code.",
    102: "Folder code must end with a lowercase letter, except for root folders.",
    103: "Folder code must start with a leading underscore.",
    104: "Folder code has multiple leading underscores.",
    105: "Folder code must start with 'F'.",
    111: "Folder name stem contains invalid characters (space, '-', '.', ...).",
    # subfolder violations
    201: "Subfolders code last letters are not consecutive lowercase letters.",
    # parser failures
    301: "File name could not be parsed.",
    302: "File name could not be validated because parent folder is invalid.",
    311: "Folder name could not be parsed.",
    312: "Folder name could not be validated because parent folder is invalid.",
    321: "Subfolders code last letters could not be validated because at least one subfolder is invalid.",  # noqa: E501
}
