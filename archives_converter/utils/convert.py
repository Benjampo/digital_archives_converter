import os
import concurrent.futures
import threading
import hashlib
import shutil
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.console import Console
from rich import print

from helpers.converters.mkv import convert_to_mkv
from helpers.converters.images import convert_images
from helpers.converters.audio import convert_audio
from helpers.converters.videos import convert_videos
from helpers.converters.text import convert_text
from helpers.delete_empty_folders import delete_empty_folders
from helpers.folders import count_files_and_folders
from utils.clone import clone_folder
from utils.rename import rename_files_and_folders
from helpers.bagit import create_data_folder_and_move_content, create_manifest, create_bagit_txt
from helpers.metadata import create_metadata_files

console = Console()

def process_file(file, root, progress, task, selected_media_types):
    if file == '.DS_Store':  # Skip .DS_Store files
        progress.update(task, advance=1)
        return

    file_path = os.path.join(root, file)
    if not os.path.exists(file_path):
        progress.update(task, advance=1, current_file=file)
        return

    progress.update(task, current_file=f"Converting {file}")

    file_name_without_ext = os.path.splitext(file)[0]
    converted_suffixes = ['_pdfa', '_tiff', '_wav', '_ffv1']
    if any(file_name_without_ext.lower().endswith(suffix) for suffix in converted_suffixes):
        print(f"Skipping already converted file: {file}")
        progress.update(task, advance=1, current_file=f"Skipped {file}")
        return
    

    if 'image' in selected_media_types:
        convert_images([file], root)
        print(f"[bold green]Converted image:[/bold green] {file_path}")
    if 'audio' in selected_media_types:
        convert_audio([file], root)
        print(f"[bold green]Converted audio:[/bold green] {file_path}")
    if 'video' in selected_media_types:
        convert_videos([file], root)
        print(f"[bold green]Converted video:[/bold green] {file_path}")
    if 'text' in selected_media_types:
        convert_text([file], root)
        print(f"[bold green]Converted text:[/bold green] {file_path}")

    progress.update(task, advance=1, current_file=f"Completed {file}")



def convert_files(destination_folder, selected_media_types):
    print("[bold cyan]Starting conversion[/bold cyan] :gear:")

    with Progress(
        SpinnerColumn(spinner_name='clock'),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("[progress.files] {task.completed}/{task.total} :file_folder:"),
        TextColumn("{task.fields[current_file]}")
    ) as progress:
        total_files, _ = count_files_and_folders(destination_folder, selected_media_types)
        convert_task = progress.add_task("[bold blue]Converting files...[/bold blue]", total=total_files, current_file="")

        update_lock = threading.Lock()
        def thread_safe_update(*args, **kwargs):
            with update_lock:
                progress.update(*args, **kwargs)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for root, dirs, files in os.walk(destination_folder):
                file_tasks = [
                    executor.submit(process_file, file, root, progress, convert_task, selected_media_types)
                    for file in files if file != '.DS_Store'
                ]
                if 'dvd' in selected_media_types:
                    if 'VIDEO_TS' in dirs:
                        video_ts_folder = os.path.join(root, 'VIDEO_TS')
                        thread_safe_update(convert_task, current_file=f"Converting VIDEO_TS: {root}")
                        convert_to_mkv([root], root)
                        print(f"[bold green]Converted VIDEO_TS:[/bold green] {root}")
                        thread_safe_update(convert_task, advance=1, current_file=f"Completed VIDEO_TS: {root}")

                concurrent.futures.wait(file_tasks)

        progress.update(convert_task, completed=total_files)

    delete_task = progress.add_task("[bold red]Deleting empty folders...[/bold red]", total=total_files)
    delete_empty_folders(destination_folder)
    progress.update(delete_task, completed=total_files)
    console.print("[bold cyan]Conversion completed![/bold cyan] :sparkles:")

def convert_folder(source_folder, selected_media_types, destination_folder=None):
    destination_folder = clone_folder(source_folder, selected_media_types, destination_folder)
    rename_files_and_folders(destination_folder, selected_media_types)
    create_metadata_files(source_folder)
    convert_files(destination_folder, selected_media_types)

    print("[bold cyan]Conversion completed. Creating BagIt structure...[/bold cyan]")

    for item in os.listdir(destination_folder):
        item_path = os.path.join(destination_folder, item)
        if os.path.isdir(item_path):
            print(f"[bold blue]Processing {item}[/bold blue]")
            create_data_folder_and_move_content(item_path)
            create_manifest(item_path)
            create_bagit_txt(item_path)

    print("[bold green]BagIt structure created![/bold green]")

