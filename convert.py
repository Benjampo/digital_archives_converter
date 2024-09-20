import os
import subprocess
import shutil
from PIL import Image
import logging
from tqdm import tqdm

from helpers.converters.images import convert_images
from helpers.converters.audio import convert_audio
from helpers.converters.videos import convert_videos
from helpers.converters.text import convert_text
from helpers.converters.mkv import convert_to_mkv
from helpers.delete_empty_folders import delete_empty_folders
from helpers.to_snake_case import to_snake_case

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def convert_folder(source_folder, destination_folder=None):
    # If no destination folder is provided, create one with "Master_" prefixed
    if destination_folder is None:
        destination_folder = os.path.join(os.path.dirname(source_folder), f"Master_{os.path.basename(source_folder)}")
    
    # Use the existing destination folder if it exists, otherwise clone the source folder
    if os.path.exists(destination_folder):
        tqdm.write(f"Using existing destination folder: {destination_folder}")
    else:
        tqdm.write(f"Cloning source folder...")
        shutil.copytree(source_folder, destination_folder)
        tqdm.write(f"Cloned source folder")

    # Get total number of files
    total_files = sum([len(files) for _, _, files in os.walk(destination_folder)])

    with tqdm(total=total_files, desc="Converting files", unit="file") as pbar:
        for root, dirs, files in os.walk(destination_folder):
            for file in files:
                # Rename file to snake_case
                new_name = to_snake_case(file)
                os.rename(os.path.join(root, file), os.path.join(root, new_name))
                
                # Perform conversions
                convert_images([new_name], root)
                convert_audio([new_name], root)
                convert_videos([new_name], root)
                convert_text([new_name], root)

                if 'VIDEO_TS' in dirs:
                    convert_to_mkv([new_name], root)

                # Update progress bar
                pbar.update(1)

    tqdm.write("Deleting empty folders...")
    delete_empty_folders(destination_folder)
    tqdm.write("Conversion complete!")

# Example usage
convert_folder('/Users/benjaminporchet/Desktop/example_folder')
