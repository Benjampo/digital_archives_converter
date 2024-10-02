import os
from datetime import datetime
import subprocess
import logging
import json
from rich import print


def create_metadata_files(destination_folder):
    for item in os.listdir(destination_folder):
        item_path = os.path.join(destination_folder, item)
        if os.path.isdir(item_path):
            metadata_file_path = os.path.join(item_path, "metadata.json")
            
            try:
                with open(metadata_file_path, "w") as metadata_file:
                    json.dump({}, metadata_file)
                print(f"Empty metadata file created: {metadata_file_path}")
            except IOError as e:
                logging.error(f"Error creating metadata file {metadata_file_path}: {str(e)}")


def extract_metadata(file_path):
    if os.path.basename(file_path) == "metadata.json":
        return ""

    try:
        exiftool_command = ['exiftool', '-j', file_path]
        result = subprocess.run(exiftool_command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"ExifTool error for {file_path}: {e.stderr}")
    except Exception as e:
        logging.error(f"Error extracting metadata from {file_path}: {str(e)}")
    return ""

def append_metadata(metadata, metadata_file, original_file_path):
    try:
        os.makedirs(os.path.dirname(metadata_file), exist_ok=True)

        existing_data = {}
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                existing_data = json.load(f)

        metadata_dict = json.loads(metadata)[0] if metadata else {}

        file_key = os.path.basename(original_file_path)
        existing_data[file_key] = {
            'metadata': metadata_dict,
            'timestamp': datetime.now().isoformat()
        }

        with open(metadata_file, 'w') as f:
            json.dump(existing_data, f, indent=2)

    except json.JSONDecodeError as e:
        logging.error(f"JSON error while appending metadata for {original_file_path}: {str(e)}")
    except IOError as e:
        logging.error(f"I/O error while appending metadata for {original_file_path}: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error while appending metadata for {original_file_path}: {str(e)}")