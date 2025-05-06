import os
from helpers.folders import copy_folder_with_progress
from rich import print
import shutil
from helpers.to_snake_case import to_snake_case
from helpers.folders import should_copy_file
from helpers.name_identifier import predict_name_based_on_extension
def clone_folder(source_folder, clone_type, selected_media_types, destination_folder=None):
    print("[bold cyan]Starting cloning[/bold cyan] :cd:")

    if destination_folder is None:
        base_name = os.path.basename(source_folder)

        if base_name.startswith("SIP_"):
            base_name = base_name[4:]
        
        if clone_type == "AIP":
            destination_folder = os.path.join(os.path.dirname(source_folder), f"AIP_{base_name}")
        elif clone_type == "DIP":
            destination_folder = os.path.join(os.path.dirname(source_folder), f"DIP_{base_name}")
        elif clone_type == "clone":
            destination_folder = os.path.join(os.path.dirname(source_folder), f"CLONE_{base_name}")
        else:
            raise ValueError(f"Invalid clone type: {clone_type}")
    
    if os.path.exists(destination_folder):
        cloning_changes_to_folder(source_folder, destination_folder, selected_media_types, clone_type)
    else:
        print("[bold yellow]Cloning source folder...[/bold yellow]")
        copy_folder_with_progress(source_folder, destination_folder, selected_media_types)
        print("[bold green]Cloned source folder[/bold green]")

    return destination_folder

    

def cloning_changes_to_folder(source_folder, destination_folder, selected_media_types, clone_type):
    print(f"[bold yellow]Cloning changes to folder...[/bold yellow]")
    folders_with_data = []
    for root, dirs, files in os.walk(destination_folder):
        if "bagit.txt" in files:
            data_dir = os.path.join(root, "data")
            if os.path.exists(data_dir):
                # Add all files from the data directory
                for data_root, data_dirs, data_files in os.walk(data_dir):
                    for data_file in data_files:
                        folders_with_data.append({
                            "file": to_snake_case(data_file),
                            "path": data_dir  # Use the actual path, not snake_case
                        })

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            new_name_file = to_snake_case(file)
            os.rename(os.path.join(root, file), os.path.join(root, new_name_file))
            if file == '.DS_Store':
                continue
            # Default target directory
            target_dir = destination_folder
            
            if folders_with_data:
                for folder in folders_with_data:
                    if file == '.DS_Store':
                        continue
                    future_name = predict_name_based_on_extension(new_name_file, clone_type)
                    if folder["file"] == future_name:  # Exact match
                        target_dir = folder["path"]
                        print(f"[bold yellow]Using specific path: {target_dir}[/bold yellow]")
                        break

            src_file = os.path.join(root, new_name_file)
            relative_path = to_snake_case(os.path.relpath(src_file, source_folder))
            dst_file = os.path.join(target_dir, new_name_file)
            print(f"Copying {src_file} to {dst_file}")
            # Check if the file exists in the destination folder
            if not os.path.exists(dst_file):
                if should_copy_file(file, selected_media_types):
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    shutil.copy2(src_file, dst_file)
            else:
                print(f"File already exists: {relative_path}")
