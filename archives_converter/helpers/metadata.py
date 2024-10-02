import os
import stat
import pwd
import grp
from datetime import datetime
from rich import print
import subprocess
import logging


def create_metadata_files(destination_folder):

    for item in os.listdir(destination_folder):
        item_path = os.path.join(destination_folder, item)
        if os.path.isdir(item_path):
            metadata_file_name = "metadata.txt"
            metadata_file_path = os.path.join(item_path, metadata_file_name)

  
            with open(metadata_file_path, "w") as metadata_file:
                pass

            print(f"Empty metadata file created: {metadata_file_path}")

def extract_metadata(file_path):
    try:
        exiftool_command = [
            'exiftool',
            file_path
        ]
        result = subprocess.run(exiftool_command, capture_output=True, text=True, check=True)
        return result.stdout
    except Exception as e:
        logging.error(f"Error extracting metadata from {file_path}: {str(e)}")
        return ""


def append_metadata(metadata, metadata_file, original_file_path):
    try:
        with open(metadata_file, 'a') as f:
            f.write(f"\n--- Metadata for {original_file_path} ---\n")
            f.write(metadata)
            f.write("\n")
    except Exception as e:
        logging.error(f"Error appending metadata for {original_file_path} to {metadata_file}: {str(e)}")

def merge_metadata_files(destination_folder):
    root_metadata_file = os.path.join(destination_folder, "metadata.txt")
    
    try:
        with open(root_metadata_file, 'w') as root_file:
            for root, dirs, files in os.walk(destination_folder):
                if "metadata.txt" in files:
                    metadata_file_path = os.path.join(root, "metadata.txt")
                    if metadata_file_path != root_metadata_file:
                        with open(metadata_file_path, 'r') as sub_file:
                            content = sub_file.read()
                            root_file.write(f"\n--- Metadata from {metadata_file_path} ---\n")
                            root_file.write(content)
                            root_file.write("\n")
                        
                        os.remove(metadata_file_path)
                        print(f"Removed: {metadata_file_path}")
        
        print(f"Merged metadata files into: {root_metadata_file}")
    except Exception as e:
        logging.error(f"Error merging metadata files: {str(e)}")
