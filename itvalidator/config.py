_FORBIDDEN_STEM_CHARACTERS: set[str] = {"-", "!", " ", "."}
_USERCODE_LENGTH: int = 3

ERRORS_CODES: dict[int, str] = {
    1: "File code does not match folder code.",
    2: "Forbidden character in file name stem ('-', '.', ...).",
    3: f"User code length is not {_USERCODE_LENGTH} characters.",
    4: "User code must be uppercase.",
}
