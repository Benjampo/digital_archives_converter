from PIL import Image
import os
import logging
import shutil
from helpers.metadata import extract_metadata, append_metadata


def convert_tiff(files, root):
    return convert_image(files, root, 'tiff')

def convert_jpg(files, root):
    return convert_image(files, root, 'jpg')

def convert_image(files, root, output_format, quality=None):
    image_extensions = ('.jpg', '.jpeg', '.tif', '.tiff', '.png', '.gif', '.bmp')
    image_files = [f for f in files if f.lower().endswith(image_extensions)]
    conversion_performed = False

    for img_file in image_files:
        input_path = os.path.join(root, img_file)
        output_ext = '.tiff' if output_format == 'tiff' else '.jpg'
        output_path = os.path.splitext(input_path)[0] + output_ext
        metadata_file = os.path.join(os.path.dirname(input_path), 'metadata.json')

        if not os.path.exists(input_path):
            logging.warning(f"Skipping {img_file}: File not found")
            continue

        original_stat = os.stat(input_path)
        metadata = extract_metadata(input_path)

        try:
            if output_format == 'tiff' and img_file.lower().endswith('.tif'):
                shutil.copy2(input_path, output_path)
                os.remove(input_path)
                print(f"Copied and renamed {img_file} to {os.path.basename(output_path)}")
            elif output_format == 'jpg' and img_file.lower().endswith(('.jpeg', '.jpg')):
                if input_path.lower() == output_path.lower():
                    continue
                output_path = os.path.splitext(input_path)[0] + '.jpg'
                shutil.copy2(input_path, output_path)
                os.remove(input_path)
                print(f"Copied and renamed {img_file} to {os.path.basename(output_path)}")
            else:
                with Image.open(input_path) as img:
                    if output_format == 'jpg':
                        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                            img = img.convert('RGB')
                        img.save(output_path, 'JPEG')
                    else:
                        img.save(output_path, output_format.upper())

            os.chmod(output_path, 0o644)
            
            # Preserve original file's metadata
            os.utime(output_path, (original_stat.st_atime, original_stat.st_mtime))
            append_metadata(metadata, metadata_file, output_path)
            
            os.remove(input_path)
            conversion_performed = True
        except Exception as e:
            logging.error(f"Error converting {img_file} to {output_format}: {str(e)}")

    return conversion_performed




