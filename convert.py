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

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



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
                shutil.copy2(src_file, dst_file)
                progress.advance(task)

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

                # Update the current file in the progress bar
                progress.update(convert_task, advance=1, current_file=file)

                # Handle image files
                convert_images([file], root)
                
                # Handle audio files
                convert_audio([file], root)
                
                # Handle classic video files
                convert_videos([file], root)
                
                # Handle text files
                convert_text([file], root)
                
                if 'VIDEO_TS' in dirs:
                    convert_to_mkv([file], root)

        # Ensure the progress bar completes
        progress.update(convert_task, completed=total_files)

    # After all conversions, delete empty folders
    delete_task = progress.add_task("[bold red]Deleting empty folders...[/bold red]", total=total_files)
    delete_empty_folders(destination_folder)
    progress.update(delete_task, completed=total_files)
    console.print("[bold cyan]Conversion completed![/bold cyan] :sparkles:")

# Example usage
convert_folder('/Users/benjaminporchet/Desktop/example_folder')
