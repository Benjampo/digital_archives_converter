import unicodedata

def to_snake_case(snake_str):
    snake_str = unicodedata.normalize('NFKD', snake_str).encode('ASCII', 'ignore').decode('ASCII')
    snake_str = snake_str.lower().replace(' ', '_').replace('-', '_')
    return snake_str

