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



def convert_folder(source_folder, destination_folder, progress_bar):
    # Example of updating the progress bar
    total_files = len(os.listdir(source_folder))
    progress_bar['maximum'] = total_files
    
    for i, file in enumerate(os.listdir(source_folder)):
        # Perform conversion (example function call)
        convert_to_mkv(os.path.join(source_folder, file), destination_folder)
        
        # Update progress bar
        progress_bar['value'] = i + 1
        progress_bar.update_idletasks()

    # After all conversions, delete empty folders
    logging.info("Deleting empty folders...")
    delete_empty_folders(destination_folder)

    logging.info(f"Conversion complete. Output folder: {destination_folder}")

    # Show the input fields and buttons again
    show_inputs()







