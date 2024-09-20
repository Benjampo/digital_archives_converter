from PIL import Image
import os
import logging

def convert_images(files, root):
    image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
    logging.info(f"Converting {len(image_files)} image files to TIFF")
    for img_file in image_files:
        input_path = os.path.join(root, img_file)
        output_path = os.path.splitext(input_path)[0] + '.tiff'
        try:
            with Image.open(input_path) as img:
                img.save(output_path, 'TIFF')
            logging.info(f"Converted {img_file} to TIFF")
            os.remove(input_path)  # Remove the original image file
        except Exception as e:
            print(f"Error converting {img_file} to TIFF: {str(e)}")