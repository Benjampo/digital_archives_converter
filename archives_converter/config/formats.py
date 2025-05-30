text_files_to_ignore = [
    "bagit.txt",
    "metadata.json",
    "bagit.txt",
    "bag_info.txt",
    "manifest_sha256.txt",
    "tagmanifest_sha256.txt",
    "bag-info.txt",
    "manifest-sha256.txt",
    "tagmanifest-sha256.txt",
]
image_extensions = [
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
    ".png",
    ".gif",
    ".bmp",
    ".heic",
    ".JPG",
    ".JPEG",
    ".TIF",
    ".TIFF",
    ".PNG",
    ".GIF",
    ".BMP",
    ".HEIC",
    ".webp",
    ".WEBP",
]
video_extensions = [
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".wmv",
    ".flv",
    ".webm",
    ".mpeg",
    ".mpg",
    ".m4v",
    ".3gp",
    ".3g2",
]
audio_extensions = [".wav", ".mp3", ".aac", ".m4a", ".flac", ".ogg", ".aif", ".aiff"]
text_extensions = [".txt", ".doc", ".docx", ".rtf", ".odt", ".pdf"]

converted_suffixes = [
    f"_{ext.split('.')[-1]}"
    for ext in image_extensions + video_extensions + audio_extensions + text_extensions
]
