import cv2
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
                # Copy file first, verify copy succeeded, then remove original
                try:
                    shutil.copy2(input_path, output_path)
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                       os.remove(input_path)
                    else:
                        raise Exception("Failed to copy file - destination file missing or empty")
                except Exception as e:
                    logging.error(f"Error copying {input_path} to {output_path}: {str(e)}")
                    if os.path.exists(output_path):
                       os.remove(output_path)
                print(f"Copied and renamed {img_file} to {os.path.basename(output_path)}")
            elif output_format == 'jpg' and img_file.lower().endswith(('.jpeg', '.jpg')):
                if input_path.lower() == output_path.lower():
                    continue
                output_path = os.path.splitext(input_path)[0] + '.jpg'
                shutil.copy2(input_path, output_path)
                os.remove(input_path)
                print(f"Copied and renamed {img_file} to {os.path.basename(output_path)}")
            else:
                # Read image using OpenCV
                img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
                if img is None:
                    raise Exception(f"Failed to read image: {input_path}")

                # Convert to RGB if needed
                if len(img.shape) == 3 and img.shape[2] == 3:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                elif len(img.shape) == 3 and img.shape[2] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

                # Save with appropriate parameters
                if output_format == 'jpg':
                    params = [cv2.IMWRITE_JPEG_QUALITY, 95] if quality is None else [cv2.IMWRITE_JPEG_QUALITY, quality]
                    cv2.imwrite(output_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR), params)
                else:  # tiff
                    cv2.imwrite(output_path, img)

            os.chmod(output_path, 0o644)
            
            # Preserve original file's metadata
            os.utime(output_path, (original_stat.st_atime, original_stat.st_mtime))
            append_metadata(metadata, metadata_file, output_path)
            if os.path.exists(output_path):
                os.remove(input_path)
                
            conversion_performed = True
        except Exception as e:
            logging.error(f"Error converting {img_file} to {output_format}: {str(e)}")

    return conversion_performed




