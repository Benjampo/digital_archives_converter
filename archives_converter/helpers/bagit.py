import os
import pkg_resources
import mimetypes
from datetime import datetime


def detect_formats(bag_dir):
    """Detects the file format types in a directory."""
    formats = set()

    for root, dirs, files in os.walk(bag_dir):
        for file in files:
            # Use mimetypes to guess the MIME type
            mime_type, _ = mimetypes.guess_type(file)
            if mime_type:
                formats.add(mime_type)

    return ", ".join(formats)


def format_bag_size(size_in_bytes):
    """Converts the bag size to MB or GB, depending on its size."""
    if size_in_bytes >= 1e9:  # If greater than 1 GB
        return f"{size_in_bytes / 1e9:.2f} GB"
    elif size_in_bytes >= 1e6:  # If greater than 1 MB
        return f"{size_in_bytes / 1e6:.2f} MB"
    else:  # If less than 1 MB
        return f"{size_in_bytes} bytes"


def create_bagit_txt(bag_dir):
    """Creates or updates the bagit.txt file with necessary information."""
    bagit_txt_path = os.path.join(bag_dir, "bagit.txt")
    bagit_version = ".".join(
        pkg_resources.get_distribution("bagit").version.split(".")[:2]
    )  # Get BagIt version, only MAJOR.MINOR otherwise it will throw error

    bagit_txt_content = f"""BagIt-Version: {bagit_version}
Version: 1.0 
Tag-File-Character-Encoding: UTF-8
"""
    try:
        with open(bagit_txt_path, "w") as f:
            f.write(bagit_txt_content)
        print(f"✅ bagit.txt created for {bag_dir}.")
    except Exception as e:
        print(f"❌ Error creating bagit.txt: {e}")


def create_bag_info(bag_dir):
    """Creates or updates the bag-info.txt file in the BagIt with specific information."""
    bag_info_path = os.path.join(bag_dir, "bag-info.txt")
    creation_date = datetime.now().strftime("%Y-%m-%d")
    bag_name = os.path.basename(bag_dir)
    bag_size = sum(
        os.path.getsize(os.path.join(root, file))
        for root, dirs, files in os.walk(bag_dir)
        for file in files
    )
    formatted_bag_size = format_bag_size(bag_size)
    formats = detect_formats(bag_dir)  # Format detection
    bagit_version = pkg_resources.get_distribution("bagit").version  # Get BagIt version
    total_files = sum(
        1 for root, dirs, files in os.walk(bag_dir) for file in files
    )  # Count the number of files in the bag

    bag_info_content = f"""Bag-Name: {bag_name}
        Bag-Size: {formatted_bag_size}
        Creation-Date: {creation_date}
        BagIt-Version: {bagit_version}
        Source-Organization: Centre des littératures en Suisse romande de l'Université de Lausanne
        Contact-Email: clsr@unil.ch
        Version: 1.0
        Bagging-Date: {creation_date}
        Format: {formats}
        Number-of-Files: {total_files}
        Checksum-Algorithm: SHA-256
    """

    if "bag-info.txt" in os.listdir(bag_dir):
        bag_info_path = os.path.join(bag_dir, "bag-info.txt")
        bag_dir_files = os.listdir(bag_dir)
        formatted_bag_size = format_bag_size(bag_size)
        modification_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bagit_version = pkg_resources.get_distribution("bagit").version
        try:
            with open(bag_info_path, "a") as f:
                f.write(f"\n--- Mise à jour du {modification_date} ---\n")
                f.write(f"BagIt-Version: {bagit_version}\n")
                f.write(f"Bag-Size: {formatted_bag_size}\n")
                f.write(f"Nombre de fichiers ajoutés: {len(bag_dir_files)}\n")

                for file in bag_dir_files:
                    f.write(f"- {file}\n")

            print(f"✅ bag-info.txt mis à jour avec {len(bag_dir_files)} fichiers")
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour de bag-info.txt : {e}")

    try:
        with open(bag_info_path, "w") as f:
            f.write(bag_info_content)
        print(f"✅ bag-info.txt created for {bag_name}.")
    except Exception as e:
        print(f"❌ Error creating bag-info.txt: {e}")
