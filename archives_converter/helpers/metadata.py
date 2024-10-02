import os
import stat
import pwd
import grp
from datetime import datetime
from rich import print
import subprocess
import logging
import yaml


def create_metadata_files(destination_folder):

    for item in os.listdir(destination_folder):
        item_path = os.path.join(destination_folder, item)
        if os.path.isdir(item_path):
            metadata_file_name = "metadata.yaml"
            metadata_file_path = os.path.join(item_path, metadata_file_name)
            
            with open(metadata_file_path, "w") as metadata_file:
                yaml.dump({}, metadata_file)

            print(f"Empty metadata file created: {metadata_file_path}")

def extract_metadata(file_path):

    if os.path.basename(file_path) == "metadata.yaml":
        return ""

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
        # Load existing YAML data
        with open(metadata_file, 'r') as f:
            existing_data = yaml.safe_load(f) or {}

        # Convert metadata string to dictionary
        metadata_dict = {}
        for line in metadata.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata_dict[key.strip()] = value.strip()

        # Add new metadata to existing data
        file_key = os.path.basename(original_file_path)
        existing_data[file_key] = {
            'metadata': metadata_dict,
            'timestamp': datetime.now().isoformat()
        }

        # Write updated YAML data
        with open(metadata_file, 'w') as f:
            yaml.dump(existing_data, f, default_flow_style=False, sort_keys=False)

    except Exception as e:
        logging.error(f"Error appending metadata for {original_file_path} to {metadata_file}: {str(e)}")

def merge_metadata_files(destination_folder):
    root_metadata_file = os.path.join(destination_folder, "metadata.yaml")
    
    try:
        merged_data = {}
        for root, dirs, files in os.walk(destination_folder):
            if "metadata.yaml" in files:
                metadata_file_path = os.path.join(root, "metadata.yaml")
                if metadata_file_path != root_metadata_file:
                    with open(metadata_file_path, 'r') as sub_file:
                        sub_data = yaml.safe_load(sub_file)
                        if sub_data:
                            merged_data.update(sub_data)
                    
                    os.remove(metadata_file_path)
                    print(f"Removed: {metadata_file_path}")
        
        with open(root_metadata_file, 'w') as root_file:
            yaml.dump(merged_data, root_file, default_flow_style=False, sort_keys=False)
        
        print(f"Merged metadata files into: {root_metadata_file}")
    except Exception as e:
        logging.error(f"Error merging metadata files: {str(e)}")
