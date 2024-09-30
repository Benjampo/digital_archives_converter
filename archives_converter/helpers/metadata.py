import os
import json

def create_metadata_file(source_folder, destination_folder):
    data_folder = os.path.join(destination_folder, "data")
    # Remove the metadata_folder creation

    all_metadata = []

    for root, _, files in os.walk(data_folder):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, data_folder)
            source_file_path = os.path.join(source_folder, relative_path)
            
            metadata = {
                "filename": file,
                "path": relative_path,
                "size": os.path.getsize(file_path),
                "last_modified": os.path.getmtime(file_path),
                "source_path": source_file_path
            }
            
            all_metadata.append(metadata)
    
    # Update the metadata file path and format
    metadata_file_path = os.path.join(destination_folder, "all_metadata.txt")
    
    with open(metadata_file_path, "w") as metadata_file:
        json.dump(all_metadata, metadata_file, indent=2)