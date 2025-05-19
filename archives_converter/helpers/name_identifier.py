from config.ignore import (
    image_extensions,
    video_extensions,
    audio_extensions,
    text_files_to_ignore,
    text_extensions,
)
from .to_snake_case import to_snake_case


def predict_name_based_on_extension(input_name, convert_type):
    # get file extension
    if "." not in input_name:  # likely a folder, no extension
        return to_snake_case(input_name)
    extension = "." + input_name.split(".")[-1]
    # replace extension based on the conversion
    if extension in image_extensions and convert_type == "AIP":
        input_name = input_name.replace(extension, "_tiff.tiff")
    elif extension in image_extensions and convert_type == "DIP":
        input_name = input_name.replace(extension, "_jpg.jpg")
    elif extension in video_extensions and convert_type == "AIP":
        input_name = input_name.replace(extension, "_ffv1.mkv")
    elif extension in video_extensions and convert_type == "DIP":
        input_name = input_name.replace(extension, "_mp4.mp4")
    elif extension in audio_extensions and convert_type == "AIP":
        input_name = input_name.replace(extension, "_wav.wav")
    elif extension in audio_extensions and convert_type == "DIP":
        input_name = input_name.replace(extension, "_mp3.mp3")
    elif extension in text_extensions:
        input_name = input_name.replace(extension, "_pdfa.pdf")
    elif extension in text_files_to_ignore:
        return input_name

    return input_name
