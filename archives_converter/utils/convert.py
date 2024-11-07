import os
import concurrent.futures
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.console import Console
from rich import print

from helpers.converters.mkv import convert_dvd_to_mkv, convert_dvd_to_mp4
from helpers.converters.images import convert_tiff, convert_jpg
from helpers.converters.audio import convert_wav, convert_mp3
from helpers.converters.videos import convert_ffv1, convert_mp4
from helpers.converters.text import convert_pdfa
from helpers.delete_empty_folders import delete_empty_folders
from helpers.folders import count_files_and_folders
from utils.clone import clone_folder
from utils.rename import rename_files_and_folders
from helpers.bagit import create_data_folder_and_move_content, create_manifest, create_bagit_txt
from helpers.metadata import create_metadata_files
from helpers.metadata_csv import create_metadata_csv, merge_metadata_files
console = Console()

def process_file(convert_type, file, root, progress, task, selected_media_types):
    if file == '.DS_Store':  # Skip .DS_Store files
        return

    file_path = os.path.join(root, file)
    parent_folder = os.path.dirname(file_path)
    if not os.path.exists(file_path):
        return

    file_name_without_ext = os.path.splitext(file)[0]
    converted_suffixes = ['_pdfa', '_tiff', '_wav', '_ffv1', '_mp4', '_mp3', '_jpg']
    if any(file_name_without_ext.lower().endswith(suffix) for suffix in converted_suffixes):
        print(f"[bold orange]Skipping:[/bold orange] {file}")
        return

    progress.update(task, current_file=f"Converting {file}")

    conversion_performed = False
    if 'image' in selected_media_types:
        if convert_type == "AIP":
            conversion_performed = convert_tiff([file], root) or conversion_performed
        elif convert_type == "DIP":
            conversion_performed = convert_jpg([file], root) or conversion_performed
    if 'audio' in selected_media_types:
        if convert_type == "AIP":
            conversion_performed = convert_wav([file], root) or conversion_performed
        elif convert_type == "DIP":
            conversion_performed = convert_mp3([file], root) or conversion_performed
    if 'video' in selected_media_types:
        if convert_type == "AIP":
            conversion_performed = convert_ffv1([file], root) or conversion_performed
        elif convert_type == "DIP":
            conversion_performed = convert_mp4([file], root) or conversion_performed
    if 'text' in selected_media_types and not file.lower() in ['bagit.txt', 'manifest-md5.txt', 'metadata.json']:
        if convert_type == "AIP":
            conversion_performed = convert_pdfa([file], root) or conversion_performed
        elif convert_type == "DIP":
            conversion_performed = convert_pdfa([file], root) or conversion_performed
    if 'dvd' in selected_media_types and file == 'VIDEO_TS':
        video_ts_folder = os.path.join(root, 'VIDEO_TS')
        progress.update(task, current_file="VIDEO_TS")
        if convert_type == "AIP":
            convert_dvd_to_mkv([root], root)
        elif convert_type == "DIP":
            convert_dvd_to_mp4([root], root)
        print(f"[bold green]Converted VIDEO_TS:[/bold green] {root}")
        video_ts_files = len([f for f in os.listdir(video_ts_folder) if f != '.DS_Store'])
        progress.update(task, advance=video_ts_files, current_file=f"Completed VIDEO_TS: {root}")
        return

    if conversion_performed:
        print(f"[bold green]:heavy_check_mark: Converted file:[/bold green] [link=file://{parent_folder}]{file_path}[/link]")
        progress.update(task, advance=1, current_file=f"Completed [link=file://{parent_folder}]{file}[/link]")


def convert_files(destination_folder, convert_type, selected_media_types):
    print("[bold cyan]Starting conversion[/bold cyan] :gear:")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("[progress.files] {task.completed}/{task.total} :file_folder:"),
        TextColumn("{task.fields[current_file]}")
    ) as progress:
        total_files, _ = count_files_and_folders(destination_folder, selected_media_types)
        convert_task = progress.add_task("[bold blue]Converting files...[/bold blue]", total=total_files, current_file="")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for root, dirs, files in os.walk(destination_folder):
                file_tasks = [
                    executor.submit(process_file,convert_type, file, root, progress, convert_task, selected_media_types)
                    for file in files + dirs if file != '.DS_Store'
                ]
                concurrent.futures.wait(file_tasks)

        final_completed = progress.tasks[convert_task].completed
        progress.update(convert_task, total=final_completed, completed=final_completed)

   



def convert_folder(source_folder,convert_type, selected_media_types, destination_folder=None):
    destination_folder = clone_folder(source_folder, convert_type, selected_media_types, destination_folder)
    rename_files_and_folders(destination_folder, selected_media_types)
    create_metadata_files(destination_folder)
    convert_files(destination_folder, convert_type, selected_media_types)

    print("[bold yellow]Creating BagIt structure...[/bold yellow]")

    items = [item for item in os.listdir(destination_folder) if os.path.isdir(os.path.join(destination_folder, item))]
    with Progress( SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("[bold blue]Creating BagIt structure...", total=len(items))
        for item in items:
            item_path = os.path.join(destination_folder, item)
            progress.update(task, description="[bold blue]Processing metadatas", current_file=f"Processing {item}")
            create_data_folder_and_move_content(item_path)
            create_manifest(item_path)
            create_bagit_txt(item_path)
            merge_metadata_files(item_path)
            progress.advance(task)
    
    print("[bold green]:heavy_check_mark: BagIt structure created![/bold green]")

    print("[bold yellow]Creating metadata HTML table...[/bold yellow]")

    create_metadata_csv(destination_folder)
    total_files, _ = count_files_and_folders(destination_folder, selected_media_types)

    delete_task = progress.add_task("[bold red]Deleting empty folders...[/bold red]", total=total_files)
    delete_empty_folders(destination_folder)
    progress.update(delete_task, completed=total_files)
    console.print("[bold green]:heavy_check_mark: Conversion completed![/bold green] :sparkles:")

    print("[bold green]:heavy_check_mark: Metadata HTML table created![/bold green]")
  


