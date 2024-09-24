import os
import shutil
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn   

def count_files_and_folders(folder):
    total_files = 0
    total_folders = 0
    for _, dirs, files in os.walk(folder):
        total_files += len(files)
        total_folders += len(dirs)
    return total_files, total_folders

def copy_folder_with_progress(source, destination):
    total_files, total_folders = count_files_and_folders(source)
    total_items = total_files + total_folders

    with Progress(
        SpinnerColumn(spinner_name='clock'),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn()
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
                src_file = os.path.join(root, file)
                dst_file = os.path.join(destination, os.path.relpath(src_file, source))
                try:
                    shutil.copy2(src_file, dst_file)
                except PermissionError as e:
                    print(f"Permission denied: {e.filename}")
                progress.advance(task)