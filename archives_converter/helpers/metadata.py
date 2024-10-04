import os
from datetime import datetime
import subprocess
import logging
import json
from rich import print


def create_metadata_files(destination_folder):
    for root, dirs, files in os.walk(destination_folder):
        metadata_file_path = os.path.join(root, "metadata.json")
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


def append_metadata(metadata, metadata_file, file_path):
    try:
        with open(metadata_file, 'r+') as f:
            try:
                existing_metadata = json.load(f)
            except json.JSONDecodeError:
                existing_metadata = {}
            
            # Parse the metadata string into a JSON object
            try:
                parsed_metadata = json.loads(metadata)
                if isinstance(parsed_metadata, list) and len(parsed_metadata) > 0:
                    parsed_metadata = parsed_metadata[0]  # Take the first item if it's a list
            except json.JSONDecodeError:
                logging.error(f"Failed to parse metadata for {file_path}")
                parsed_metadata = {"error": "Failed to parse metadata"}

            # Get the relative path from the data folder
            data_folder = os.path.dirname(metadata_file)
            relative_path = os.path.relpath(file_path, data_folder)

            # Append new metadata using the relative path as the key
            existing_metadata[relative_path] = parsed_metadata
            
            # Move file pointer to the beginning and truncate the file
            f.seek(0)
            f.truncate()
            
            # Write updated metadata
            json.dump(existing_metadata, f, indent=2)
    except Exception as e:
        logging.error(f"Error appending metadata for {file_path}: {str(e)}")