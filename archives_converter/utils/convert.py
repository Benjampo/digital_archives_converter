import os
import concurrent.futures
import threading
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

console = Console()

def process_file(file, root, progress, task):
    if file == '.DS_Store':  # Skip .DS_Store files
        return

    file_path = os.path.join(root, file)
    if not os.path.exists(file_path):
        progress.update(task, advance=1, current_file=file)
        return

    progress.update(task, current_file=f"Converting {file}")

    convert_images([file], root)
    convert_audio([file], root)
    convert_videos([file], root)
    convert_text([file], root)
    print(f"[bold green]Converted file:[/bold green] {file_path}")

    progress.update(task, advance=1, current_file=f"Completed {file}")

def convert_files(folder):
    print("[bold cyan]Starting conversion[/bold cyan] :gear:")

    with Progress(
        SpinnerColumn(spinner_name='clock'),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("[progress.files] {task.completed}/{task.total} :file_folder:"),
        TextColumn("{task.fields[current_file]}")
    ) as progress:
        total_files, _ = count_files_and_folders(folder)
        convert_task = progress.add_task("[bold blue]Converting files...[/bold blue]", total=total_files, current_file="")

        update_lock = threading.Lock()
        def thread_safe_update(*args, **kwargs):
            with update_lock:
                progress.update(*args, **kwargs)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for root, dirs, files in os.walk(folder):
                file_tasks = [
                    executor.submit(process_file, file, root, progress, convert_task)
                    for file in files if file != '.DS_Store'
                ]

                if 'VIDEO_TS' in dirs:
                    video_ts_parent = os.path.dirname(root)
                    thread_safe_update(convert_task, current_file=f"Converting VIDEO_TS: {video_ts_parent}")
                    convert_to_mkv([video_ts_parent], video_ts_parent)
                    print(f"[bold green]Converted VIDEO_TS:[/bold green] {video_ts_parent}")
                    thread_safe_update(convert_task, advance=1, current_file=f"Completed VIDEO_TS: {video_ts_parent}")

                concurrent.futures.wait(file_tasks)

        progress.update(convert_task, completed=total_files)

    delete_task = progress.add_task("[bold red]Deleting empty folders...[/bold red]", total=total_files)
    delete_empty_folders(folder)
    progress.update(delete_task, completed=total_files)
    console.print("[bold cyan]Conversion completed![/bold cyan] :sparkles:")

def convert_folder(source_folder, destination_folder=None):
    destination_folder = clone_folder(source_folder, destination_folder)
    rename_files_and_folders(destination_folder)
    convert_files(destination_folder)

