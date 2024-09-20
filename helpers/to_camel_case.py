def to_camel_case(snake_str):
    snake_str = snake_str.lower() 
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])