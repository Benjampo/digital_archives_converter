import unicodedata
import re
import os

def to_snake_case(file_name):
    # Split the file name and extension
    name, ext = os.path.splitext(file_name)

    # Convert the name part to snake case
    snake_str = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    snake_str = snake_str.lower()
    snake_str = re.sub(r"['\s\-.,;:!?&]+", '_', snake_str)
    snake_str = re.sub(r'^_+|_+$', '', snake_str)
    snake_str = re.sub(r'_+', '_', snake_str)
    
    # Combine the snake case name with the original extension
    return snake_str + ext

