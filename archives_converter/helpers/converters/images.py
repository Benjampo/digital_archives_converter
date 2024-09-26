from PIL import Image
import os
import logging

def convert_images(files, root):
    image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.tif', '.png', '.gif', '.bmp'))]
    for img_file in image_files:
        input_path = os.path.join(root, img_file)
        output_path = os.path.splitext(input_path)[0] + '.tiff'
        
        if not os.path.exists(input_path):
            logging.warning(f"Skipping {img_file}: File not found")
            continue
        
        # If the file is already a TIFF, just rename it
        if img_file.lower().endswith(('.tif')):
            try:
                os.rename(input_path, output_path)
                os.chmod(output_path, 0o644)  # Set permissions to rw-r--r--
                print(f"Renamed {img_file} to {os.path.basename(output_path)}")
            except OSError as e:
                logging.error(f"Error renaming {img_file}: {str(e)}")
            continue
        
        try:
            with Image.open(input_path) as img:
                img.save(output_path, 'TIFF')
            os.chmod(output_path, 0o644)  # Set permissions to rw-r--r--
            os.remove(input_path)  # Remove the original image file
        except Exception as e:
            logging.error(f"Error converting {img_file} to TIFF: {str(e)}")
