import os
import subprocess
import shutil
from PIL import Image
import logging
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.console import Console

console = Console()

from helpers.converters.images import convert_images
from helpers.converters.audio import convert_audio
from helpers.converters.videos import convert_videos
from helpers.converters.text import convert_text
from helpers.converters.mkv import convert_to_mkv
from helpers.delete_empty_folders import delete_empty_folders
from helpers.to_snake_case import to_snake_case
from helpers.folders import count_files_and_folders, copy_folder_with_progress




def convert_folder(source_folder, destination_folder=None):
    print("[bold cyan]Starting conversion[/bold cyan] :cd:")

    # If no destination folder is provided, create one with "Master_" prefixed
    if destination_folder is None:
        destination_folder = os.path.join(os.path.dirname(source_folder), f"Master_{os.path.basename(source_folder)}")
    
    # Use the existing destination folder if it exists, otherwise clone the source folder
    if os.path.exists(destination_folder):
        print(f"[bold green]Using existing destination folder:[/bold green] [italic]{destination_folder}[/italic]")
    else:
        print(f"[bold yellow]Cloning source folder...[/bold yellow]")
        copy_folder_with_progress(source_folder, destination_folder)
        print(f"[bold green]Cloned source folder[/bold green]")

    # Check for duplicate filenames (without extensions) and rename if necessary
    for root, dirs, files in os.walk(destination_folder):
        name_count = {}
        for file in files:
            if file == '.DS_Store':  # Skip .DS_Store files
                continue
            name, ext = os.path.splitext(file)
            if name in name_count:
                name_count[name] += 1
                new_name = f"{name}_{name_count[name]}{ext}"
                os.rename(os.path.join(root, file), os.path.join(root, new_name))
            else:
                name_count[name] = 0

    # Walk through the cloned folder and rename files with progress bar
    with Progress(
        SpinnerColumn(spinner_name='clock'),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn()
    ) as progress:
        total_files, _ = count_files_and_folders(destination_folder)
        rename_task = progress.add_task("[bold blue]Renaming files...[/bold blue]", total=total_files)

        for root, dirs, files in os.walk(destination_folder):
            for file in files:
                if file == '.DS_Store':  # Skip .DS_Store files
                    continue
                new_name = to_snake_case(file)
                os.rename(os.path.join(root, file), os.path.join(root, new_name))
                progress.advance(rename_task)

        # Ensure the progress bar completes
        progress.update(rename_task, completed=total_files)

    # Walk through the cloned folder and convert files with progress bar
    with Progress(
        SpinnerColumn(spinner_name='clock'),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("[progress.files] {task.completed}/{task.total} :file_folder:"),
        TextColumn("[progress.current_file] {task.fields[current_file]}")
    ) as progress:
        total_files, _ = count_files_and_folders(destination_folder)
        convert_task = progress.add_task("[bold blue]Converting files...[/bold blue]", total=total_files, current_file="")

        for root, dirs, files in os.walk(destination_folder):
            for file in files:
                if file == '.DS_Store':  # Skip .DS_Store files
                    continue

                progress.update(convert_task, advance=1, current_file=file)

                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    convert_images([file], root)
                    convert_audio([file], root)
                    convert_videos([file], root)
                    convert_text([file], root)

            # Check for VIDEO_TS directory and convert it
            if 'VIDEO_TS' in dirs:
                video_ts_path = os.path.join(root, 'VIDEO_TS')
                video_ts_files = [os.path.join(video_ts_path, f) for f in os.listdir(video_ts_path) if os.path.isfile(os.path.join(video_ts_path, f))]
                total_files += len(video_ts_files)  # Add VIDEO_TS files to the total count
                convert_to_mkv([video_ts_path], root
                progress.update(convert_task, advance=len(video_ts_files), current_file='VIDEO_TS')

        # Ensure the progress bar completes
        progress.update(convert_task, completed=total_files)

    # After all conversions, delete empty folders
    delete_task = progress.add_task("[bold red]Deleting empty folders...[/bold red]", total=total_files)
    delete_empty_folders(destination_folder)
    progress.update(delete_task, completed=total_files)
    console.print("[bold cyan]Conversion completed![/bold cyan] :sparkles:")

# Example usage
convert_folder('/Users/benjaminporchet/Desktop/sample')
