import unicodedata
import re
import os
from config.formats import text_files_to_ignore


def to_snake_case(file_path):
    # ignore files existing
    if any(ignore_str in file_path for ignore_str in text_files_to_ignore):
        splitted_path = file_path.split("/")
        if len(splitted_path) > 1:
            made_parts = [
                to_snake_case(splitted_path) for splitted_path in splitted_path
            ]
            return "/".join(made_parts)

        return file_path

    else:
        name, ext = os.path.splitext(file_path)

        snake_str = (
            unicodedata.normalize("NFKD", name)
            .encode("ASCII", "ignore")
            .decode("ASCII")
        )
        snake_str = re.sub(r"['\"\s\-,;:!?&$()#]+", "_", snake_str)
        snake_str = re.sub(r"^_+|_+$", "", snake_str)
        snake_str = re.sub(r"_+", "_", snake_str)

        return snake_str + ext
