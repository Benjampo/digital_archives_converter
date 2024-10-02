import os
from datetime import datetime
import subprocess
import logging
import yaml
from rich import print


def create_metadata_files(destination_folder):
    for item in os.listdir(destination_folder):
        item_path = os.path.join(destination_folder, item)
        if os.path.isdir(item_path):
            metadata_file_path = os.path.join(item_path, "metadata.yaml")
            
            try:
                with open(metadata_file_path, "w") as metadata_file:
                    yaml.dump({}, metadata_file)
                print(f"Empty metadata file created: {metadata_file_path}")
            except IOError as e:
                logging.error(f"Error creating metadata file {metadata_file_path}: {str(e)}")


def extract_metadata(file_path):
    if os.path.basename(file_path) == "metadata.yaml":
        return ""

    try:
        exiftool_command = ['exiftool', file_path]
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
                existing_data = yaml.safe_load(f) or {}

        metadata_dict = {}
        for line in metadata.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                value = value.strip().strip('"\'').replace('\n', ' ')
                metadata_dict[key.strip()] = value

        file_key = os.path.basename(original_file_path)
        existing_data[file_key] = {
            'metadata': metadata_dict,
            'timestamp': datetime.now().isoformat()
        }

        with open(metadata_file, 'w') as f:
            yaml.dump(existing_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)

    except yaml.YAMLError as e:
        logging.error(f"YAML error while appending metadata for {original_file_path}: {str(e)}")
    except IOError as e:
        logging.error(f"I/O error while appending metadata for {original_file_path}: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error while appending metadata for {original_file_path}: {str(e)}")

