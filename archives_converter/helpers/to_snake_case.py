import unicodedata
import re
import os
from config.ignore import text_files_to_ignore


def to_snake_case(file_name):
    # ignore files existing
    if any(ignore_str in file_name for ignore_str in text_files_to_ignore):
        return file_name

    name, ext = os.path.splitext(file_name)

    snake_str = (
        unicodedata.normalize("NFKD", name).encode("ASCII", "ignore").decode("ASCII")
    )
    snake_str = re.sub(r"['\"\s\-,;:!?&$()#]+", "_", snake_str)
    snake_str = re.sub(r"^_+|_+$", "", snake_str)
    snake_str = re.sub(r"_+", "_", snake_str)

    return snake_str + ext
