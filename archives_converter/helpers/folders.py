import os
import shutil
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    SpinnerColumn,
)


def count_files_and_folders(folder, selected_media_types):
    total_files = 0
    total_folders = 0
    for root, dirs, files in os.walk(folder):
        total_folders += len(dirs)
        for file in files:
            if should_copy_file(file, selected_media_types):
                total_files += 1
    return total_files, total_folders


def should_copy_file(file, selected_media_types):
    lower_file = file.lower()
    if "dvd" in selected_media_types and lower_file.endswith((".vob", ".ifo", ".bup")):
        return True
    if "audio" in selected_media_types and lower_file.endswith(
        (
            ".mp3",
            ".aac",
            ".m4a",
            ".m4p",
            ".flac",
            ".ogg",
            ".aif",
            ".aiff",
            ".wav",
            ".wma",
            ".alac",
        )
    ):
        return True
    if "video" in selected_media_types and lower_file.endswith(
        (
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
        )
    ):
        return True
    if "image" in selected_media_types and lower_file.endswith(
        (
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".tiff",
            ".tif",
            ".bmp",
            ".webp",
            ".psd",
            ".svg",
            ".heic",
            ".raw",
            ".cr2",
            ".nef",
            ".orf",
            ".sr2",
        )
    ):
        return True
    if "text" in selected_media_types and lower_file.endswith(
        (".txt", ".pdf", ".doc", ".docx", ".rtf", ".odt", ".tex", ".wpd")
    ):
        return True
    return False


def copy_folder_with_progress(source, destination, selected_media_types):
    total_files, total_folders = count_files_and_folders(source, selected_media_types)
    total_items = total_files + total_folders

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task("Copying folder...", total=total_items)

        for root, dirs, files in os.walk(source):
            # Create directories in the destination folder
            for dir in dirs:
                src_dir = os.path.join(root, dir)
                dst_dir = os.path.join(destination, os.path.relpath(src_dir, source))
                os.makedirs(dst_dir, exist_ok=True)
                progress.advance(task)

            # Copy files to the destination folder
            for file in files:
                if should_copy_file(file, selected_media_types):
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(
                        destination, os.path.relpath(src_file, source)
                    )

                    try:
                        shutil.copy2(src_file, dst_file)
                    except PermissionError as e:
                        print(f"Permission denied: {e.filename}")
                    progress.advance(task)
