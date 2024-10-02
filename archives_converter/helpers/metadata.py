import os
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
        os.makedirs(os.path.dirname(metadata_file), exist_ok=True)

        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                existing_data = yaml.safe_load(f) or {}
        else:
            existing_data = {}

        metadata_dict = {}
        for line in metadata.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)

                value = value.strip().strip('"\'')

                value = value.replace('\n', ' ')
                metadata_dict[key.strip()] = value

        file_key = os.path.basename(original_file_path)
        existing_data[file_key] = {
            'metadata': metadata_dict,
            'timestamp': datetime.now().isoformat()
        }

        with open(metadata_file, 'w') as f:
            yaml.dump(existing_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)

    except Exception as e:
        logging.error(f"Error appending metadata for {original_file_path} to {metadata_file}: {str(e)}")


