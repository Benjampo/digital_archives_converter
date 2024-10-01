import os
import stat
import pwd
import grp
from datetime import datetime
from rich import print
from rich.prompt import Confirm


def create_metadata_files(source_folder, destination_folder):

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

    for item in os.listdir(destination_folder):
        dest_item_path = os.path.join(destination_folder, item)
        if os.path.isdir(dest_item_path):
            folder_metadata = []

            for root, dirs, files in os.walk(dest_item_path):
                for file in files:
                    if file.lower().endswith('.txt') and file.lower() in ['metadata.txt', 'manifest-md5.txt', 'bagit.txt']:
                        continue
                
                    file_path = os.path.join(root, file)
                    file_stat = os.stat(file_path)
                    relative_path = os.path.relpath(file_path, dest_item_path)
                    

                    file_metadata = {
                        "name": os.path.join(item, relative_path),
                        "size": file_stat.st_size,
                        "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        "accessed": datetime.fromtimestamp(file_stat.st_atime).isoformat(),
                        "mode": stat.filemode(file_stat.st_mode),
                        "uid": file_stat.st_uid,
                        "user": pwd.getpwuid(file_stat.st_uid).pw_name,
                        "gid": file_stat.st_gid,
                        "group": grp.getgrgid(file_stat.st_gid).gr_name,
                        "inode": file_stat.st_ino,
                        "links": file_stat.st_nlink,
                    }
                    folder_metadata.append(file_metadata)

            metadata_file_name = "metadata.txt"
            metadata_file_path = os.path.join(dest_item_path, metadata_file_name)

            with open(metadata_file_path, "w") as metadata_file:
                for item in folder_metadata:
                    metadata_file.write(f"File: {item['name']}\n")
                    metadata_file.write(f"  Size: {item['size']} bytes\n")
                    metadata_file.write(f"  Created: {item['created']}\n")
                    metadata_file.write(f"  Modified: {item['modified']}\n")
                    metadata_file.write(f"  Accessed: {item['accessed']}\n")
                    metadata_file.write(f"  Mode: {item['mode']}\n")
                    metadata_file.write(f"  UID: {item['uid']} ({item['user']})\n")
                    metadata_file.write(f"  GID: {item['gid']} ({item['group']})\n")
                    metadata_file.write(f"  Inode: {item['inode']}\n")
                    metadata_file.write(f"  Hard Links: {item['links']}\n")
                    metadata_file.write("\n")

            print(f"Metadata file created: {metadata_file_path}")

    print(f"Metadata files created successfully in {master_folder}")