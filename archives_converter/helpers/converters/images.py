from PIL import Image
import os
import logging
import shutil
from helpers.metadata import extract_metadata, append_metadata

def convert_images(files, root):
    metadata_file = os.path.join(root, 'metadata.yaml')
    image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.tif', '.png', '.gif', '.bmp'))]
    for img_file in image_files:
        input_path = os.path.join(root, img_file)
        output_path = os.path.splitext(input_path)[0] + '_tiff.tiff'
        
        if not os.path.exists(input_path):
            logging.warning(f"Skipping {img_file}: File not found")
            continue
        
        # Get original file metadata
        original_stat = os.stat(input_path)
        
        # Extract metadata before conversion
        metadata = extract_metadata(input_path)
        
        # If the file is already a TIFF, just rename it
        if img_file.lower().endswith(('.tif')):
            try:
                shutil.copy2(input_path, output_path)  # Copy file with metadata
                os.remove(input_path)  # Remove the original file
                os.chmod(output_path, 0o644)  # Set permissions to rw-r--r--
                print(f"Copied and renamed {img_file} to {os.path.basename(output_path)}")
            except OSError as e:
                logging.error(f"Error renaming {img_file}: {str(e)}")
            continue
        
        try:
            with Image.open(input_path) as img:
                img.save(output_path, 'TIFF')
            os.chmod(output_path, 0o644)  # Set permissions to rw-r--r--
            
            # Preserve original file's metadata
            os.utime(output_path, (original_stat.st_atime, original_stat.st_mtime))
            
         
            append_metadata(metadata, metadata_file, output_path)
            
            os.remove(input_path)  # Remove the original image file
        except Exception as e:
            logging.error(f"Error converting {img_file} to TIFF: {str(e)}")

