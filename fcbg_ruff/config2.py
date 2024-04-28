import re

_FORBIDDEN_STEM_CHARACTERS: set[str] = {"-", "!", " ", "."}
_USERCODE_LENGTH: int = 3
_PATTERN = re.compile(r"_F\d+[a-z]*_.*_[A-Z]{3,4}")


ERRORS_CODES: dict[int, str] = {
    # file violations
    1: "File pattern does not match expected pattern.",
    2: "Parent folder pattern does not match expected pattern.",
    # file/folder code violation
    11: "File/Folder code must start with an 'F' in upper case.",
    # parser failures
    301: "File name could not be parsed.",
    302: "File name could not be validated because parent folder is invalid.",
}
