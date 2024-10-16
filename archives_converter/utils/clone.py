import os
from helpers.folders import copy_folder_with_progress
from rich import print

def clone_folder(source_folder, clone_type, selected_media_types, destination_folder=None):
    print("[bold cyan]Starting cloning[/bold cyan] :cd:")

    if destination_folder is None:
        if clone_type == "AIP":
            destination_folder = os.path.join(os.path.dirname(source_folder), f"AIP_{os.path.basename(source_folder)}")
        elif clone_type == "DIP":
            destination_folder = os.path.join(os.path.dirname(source_folder), f"DIP_{os.path.basename(source_folder)}")
        elif clone_type == "clone":
            destination_folder = os.path.join(os.path.dirname(source_folder), f"CLONE_{os.path.basename(source_folder)}")
        else:
            raise ValueError(f"Invalid clone type: {clone_type}")
    
    if os.path.exists(destination_folder):
        print(f"[bold green]Using existing destination folder:[/bold green] [italic]{destination_folder}[/italic]")
    else:
        print(f"[bold yellow]Cloning source folder...[/bold yellow]")
        copy_folder_with_progress(source_folder, destination_folder, selected_media_types)
        print(f"[bold green]Cloned source folder[/bold green]")

    return destination_folder