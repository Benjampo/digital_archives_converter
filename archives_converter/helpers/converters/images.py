import os
import logging
import shutil

# from helpers.metadata import extract_metadata, append_metadata
from PIL import Image
from pillow_heif import register_heif_opener

# Register HEIF/HEIC format support
register_heif_opener()


def convert_tiff(files, root):
    return convert_image(files, root, "tiff")


def convert_jpg(files, root):
    return convert_image(files, root, "jpg")


def convert_image(files, root, output_format, quality=None):
    image_extensions = (
        ".jpg",
        ".jpeg",
        ".tif",
        ".tiff",
        ".png",
        ".gif",
        ".bmp",
        ".heic",
    )
    image_files = [f for f in files if f.lower().endswith(image_extensions)]
    conversion_performed = False

    for img_file in image_files:
        input_path = os.path.join(root, img_file)
        output_ext = ".tiff" if output_format == "tiff" else ".jpg"
        extension = os.path.splitext(input_path)[1].lower().lstrip(".")
        output_path = os.path.splitext(input_path)[0] + f"_{extension}{output_ext}"
        # metadata_file = os.path.join(os.path.dirname(input_path), "metadata.json")

        if not os.path.exists(input_path):
            logging.warning(f"Skipping {img_file}: File not found")
            continue

        original_stat = os.stat(input_path)
        # metadata = extract_metadata(input_path)

        if output_format == "tiff" and img_file.lower().endswith(".tif"):
            # Copy file first, verify copy succeeded, then remove original
            try:
                shutil.copy2(input_path, output_path)
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    os.remove(input_path)
                    conversion_performed = True
                else:
                    raise Exception(
                        "Failed to copy file - destination file missing or empty"
                    )
            except Exception as e:
                logging.error(f"Error copying {input_path} to {output_path}: {str(e)}")
                if os.path.exists(output_path):
                    os.remove(output_path)
                continue  # Skip the rest of the processing for this file
        elif output_format == "jpg" and img_file.lower().endswith((".jpeg", ".jpg")):
            extension = os.path.splitext(input_path)[1].lower().lstrip(".")
            output_path = os.path.splitext(input_path)[0] + f"_{extension}.jpg"
            shutil.copy2(input_path, output_path)
            os.remove(input_path)
            conversion_performed = True
        else:
            # Open image with Pillow to preserve color profiles
            with Image.open(input_path) as pil_img:
                # Save with appropriate parameters
                if output_format == "jpg":
                    jpeg_quality = 95 if quality is None else quality
                    pil_img.save(
                        output_path,
                        format="JPEG",
                        quality=jpeg_quality,
                        icc_profile=pil_img.info.get("icc_profile"),
                    )
                elif output_format == "tiff":
                    # Preserve ICC profile for TIFF files
                    pil_img.save(
                        output_path,
                        format="TIFF",
                        compression="tiff_lzw",
                        icc_profile=pil_img.info.get("icc_profile"),
                    )

            os.chmod(output_path, 0o644)

            # Preserve original file's metadata
            os.utime(output_path, (original_stat.st_atime, original_stat.st_mtime))
            # append_metadata(metadata, metadata_file, output_path)

            # Remove input file after successful conversion
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                os.remove(input_path)
                conversion_performed = True

    return conversion_performed
