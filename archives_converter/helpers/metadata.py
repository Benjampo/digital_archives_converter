import os
from datetime import datetime
from rich import print
from rich.prompt import Confirm


def create_metadata_files(source_folder):
    # Find the Master_ folder
    source_folder_name = os.path.basename(source_folder)
    master_folder_name = f"Master_{source_folder_name}"
    parent_dir = os.path.dirname(source_folder)
    master_folder = os.path.join(parent_dir, master_folder_name)
    
    if not os.path.isdir(master_folder):
        print(f"[bold red]Error: No {master_folder_name} folder found at the same level as the selected directory.[/bold red]")
        rerun = Confirm.ask("Do you want to rerun the main script to create the Master folder?")
        if rerun:
            from utils.dialog import dialog
            dialog()
        return

    print(f"Creating metadata files in: {master_folder}")

    for item in os.listdir(master_folder):
        item_path = os.path.join(master_folder, item)
        if os.path.isdir(item_path):
            folder_metadata = []


            for root, dirs, files in os.walk(item_path):
                # Process only files
                for file in files:
                    if file.lower().endswith('.txt') and file.lower() in ['metadata.txt', 'manifest-md5.txt', 'bagit.txt']:
                        continue
                    
                    file_path = os.path.join(root, file)
                    file_stat = os.stat(file_path)
                    relative_path = os.path.relpath(file_path, item_path)
                    file_metadata = {
                        "name": relative_path,
                        "size": file_stat.st_size,
                        "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                    }
                    folder_metadata.append(file_metadata)

            # Create metadata file for the top-level directory
            metadata_file_name = "metadata.txt"
            metadata_file_path = os.path.join(item_path, metadata_file_name)
            
            with open(metadata_file_path, "w") as metadata_file:
                for item in folder_metadata:
                    metadata_file.write(f"File: {item['name']}\n")
                    metadata_file.write(f"  Size: {item['size']} bytes\n")
                    metadata_file.write(f"  Created: {item['created']}\n")
                    metadata_file.write(f"  Modified: {item['modified']}\n")
                    metadata_file.write("\n")

            print(f"Metadata file created: {metadata_file_path}")

    print(f"Metadata files created successfully in {master_folder}")