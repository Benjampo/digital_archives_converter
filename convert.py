import os
import subprocess
import shutil
import logging
from helpers.converters.images import convert_to_images
from helpers.converters.audio import convert_to_audio
from helpers.converters.videos import convert_to_videos
from helpers.converters.mkv import convert_to_mkv
from helpers.delete_empty_folders import delete_empty_folders

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def convert_folder(source_folder, destination_folder=None):
    # Use the source folder if destination folder is not provided
    if destination_folder is None:
        destination_folder = os.path.join(os.path.dirname(source_folder), 'Master_' + os.path.basename(source_folder))
        add_master_prefix = False
    else:
        add_master_prefix = False

    # Use the existing destination folder if it exists, otherwise clone the source folder
    if os.path.exists(destination_folder):
        print(f"Using existing destination folder: {destination_folder}")
    else:
        print(f"Cloning source folder to: {destination_folder}")
        shutil.copytree(source_folder, destination_folder)
        print(f"Cloned source folder to: {destination_folder}")

    # Count total files to be converted
    total_files = 0
    for root, dirs, files in os.walk(destination_folder):
        total_files += len([f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp3', '.aac', '.m4a', '.flac', '.ogg', '.m4p', '.aif', '.aiff', '.mp4', '.avi', '.mov', '.wmv', '.flv'))])
        if 'VIDEO_TS' in dirs:
            video_ts_path = os.path.join(root, 'VIDEO_TS')
            total_files += len([f for f in os.listdir(video_ts_path) if f.endswith('.VOB')])

    progress_bar['maximum'] = total_files
    progress_bar['value'] = 0

    # Walk through the cloned folder
    for root, dirs, files in os.walk(destination_folder):
        
        # Handle image files
        convert_to_images(root, destination_folder)
            
        # Handle audio files
        convert_to_audio(root, destination_folder)
            
        # Handle classic video files
        convert_to_videos(root, destination_folder)

        if 'VIDEO_TS' in dirs:
            convert_to_mkv(root, destination_folder)

    # After all conversions, delete empty folders
    logging.info("Deleting empty folders...")
    delete_empty_folders(destination_folder)

    logging.info(f"Conversion complete. Output folder: {destination_folder}")

    # Show the input fields and buttons again
    show_inputs()







