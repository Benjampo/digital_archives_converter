from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
import os
from helpers.bagit import create_bag_info, create_bagit_txt
import bagit

def apply_bag(destination_folder):
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
            bagit.make_bag(item_path, checksums=["sha256"])
            # create_data_folder_and_move_content(item_path)
            # create_manifest(item_path)
            create_bagit_txt(item_path)
            create_bag_info(item_path)
            progress.advance(task)
    
    print("[bold green]:heavy_check_mark: BagIt structure created![/bold green]")