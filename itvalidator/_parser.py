def parse_folder_name(folder: str) -> tuple[str, str]:
    """Parse the folder name.

    Parameters
    ----------
    folder : str
        Folder name, as returned by a pathlib.Path object with the .name attribute.

    Returns
    -------
    code : str
        Folder code, without the leading underscore.
    name : str
        Folder name.

    Examples
    --------
    >>> parse_folder_name("_F1_My_folder")
    ("F1", "My_folder")

    >>> parse_folder_name("_F2b_My_second_folder")
    ("F2b", "My_second_folder")
    """
    while folder.startswith("_"):
        folder = folder.removeprefix("_")
    elts = folder.split("_")
    code = elts[0]
    name = "_".join(elts[1:])
    if len(name) == 0:
        raise RuntimeError("Folder name could not be parsed.")
    return code, name


def parse_file_stem(stem: str) -> tuple[str, str, str, str]:
    """Parse the file stem.

    Parameters
    ----------
    stem : str
        File name stem, as returned by a pathlib.Path object with the .stem attribute.
        The file name stem does not contain the extension/suffix.

    Returns
    -------
    code : str
        File code.
    date : str
        File date, in the format 'YYMMDD'.
    name : str
        File name.
    usercode : str
        File user code.

    Examples
    --------
    >>> parse_file_stem("F1_220101_file_ABC")
    ("F1", "220101", "file", "ABC")

    >>> parse_file_stem("F2b_220101_My_second_file_DEF")
    ("F2b", "220101", "My_second_file", "DEF")
    """
    elts = stem.split("_")
    code = elts[0]
    date = elts[1]
    name = "_".join(elts[2:-1])
    usercode = elts[-1]
    return code, date, name, usercode
