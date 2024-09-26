import unicodedata
import re

def to_snake_case(snake_str):
    snake_str = unicodedata.normalize('NFKD', snake_str).encode('ASCII', 'ignore').decode('ASCII')
    snake_str = snake_str.lower()
    snake_str = re.sub(r'[\s\-.,;:!?]+', '_', snake_str)
    snake_str = re.sub(r'^_+|_+$', '', snake_str)
    snake_str = re.sub(r'_+', '_', snake_str)
    
    return snake_str

