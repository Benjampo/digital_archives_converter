import hashlib
import os
import shutil
import pkg_resources
import mimetypes
from datetime import datetime

def create_data_folder_and_move_content(folder):
    data_folder = os.path.join(folder, "data")
    os.makedirs(data_folder, exist_ok=True)
    
    for item in os.listdir(folder):
        if item not in ["data", "metadata.json"]:
            item_path = os.path.join(folder, item)
            shutil.move(item_path, data_folder)

def generate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def create_manifest(folder):
    manifest_path = os.path.join(folder, "manifest-md5.txt")
    with open(manifest_path, "w") as manifest:
        for root, _, files in os.walk(folder):
            # Skip hidden folders
            if any(part.startswith('.') for part in root.split(os.sep)):
                continue
            for file in files:
                if not file.startswith('.') and file not in ["manifest-md5.txt", "metadata.json"]:
                    file_path = os.path.join(root, file)
                    md5_hash = generate_md5(file_path)
                    relative_path = os.path.relpath(file_path, folder)
                    manifest.write(f"{md5_hash}  {relative_path}\n")

def detect_formats(bag_dir):
    """Détecte les types de formats des fichiers dans un répertoire."""
    formats = set()

    for root, dirs, files in os.walk(bag_dir):
        for file in files:
            # Utiliser mimetypes pour deviner le type MIME
            mime_type, _ = mimetypes.guess_type(file)
            if mime_type:
                formats.add(mime_type)
    
    return ", ".join(formats)

def format_bag_size(size_in_bytes):
    """Convertit la taille du bag en Mo ou Go, selon sa taille."""
    if size_in_bytes >= 1e9:  # Si supérieur à 1 Go
        return f"{size_in_bytes / 1e9:.2f} GB"
    elif size_in_bytes >= 1e6:  # Si supérieur à 1 Mo
        return f"{size_in_bytes / 1e6:.2f} MB"
    else:  # Si inférieur à 1 Mo
        return f"{size_in_bytes} bytes"


def create_bagit_txt(bag_dir):
    """Crée ou met à jour le fichier bagit.txt avec les informations nécessaires."""
    bagit_txt_path = os.path.join(bag_dir, "bagit.txt")
    bagit_version = pkg_resources.get_distribution("bagit").version # Récupération de la version de BagIt
    bagit_txt_content = f"""BagIt-Version: {bagit_version}
Version: 1.0 
Tag-File-Character-Encoding: UTF-8
"""
    try:
        with open(bagit_txt_path, "w") as f:
            f.write(bagit_txt_content)
        print(f"✅ bagit.txt créé pour {bag_dir}.")
    except Exception as e:
        print(f"❌ Erreur lors de la création de bagit.txt : {e}")

def create_bag_info(bag_dir):
    """Crée ou met à jour le fichier bag-info.txt dans le BagIt avec des informations spécifiques."""
    bag_info_path = os.path.join(bag_dir, "bag-info.txt")
    creation_date = datetime.now().strftime("%Y-%m-%d")
    bag_name = os.path.basename(bag_dir)
    bag_size = sum(os.path.getsize(os.path.join(root, file)) for root, dirs, files in os.walk(bag_dir) for file in files)
    formatted_bag_size = format_bag_size(bag_size)
    formats = detect_formats(bag_dir)  # Détection des formats
    bagit_version = pkg_resources.get_distribution("bagit").version # Récupération de la version de BagIt
    total_files = sum(1 for root, dirs, files in os.walk(bag_dir) for file in files) # Comptage du nombre de fichiers dans le bag

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

    try:
        with open(bag_info_path, "w") as f:
            f.write(bag_info_content)
        print(f"✅ bag-info.txt créé pour {bag_name}.")
    except Exception as e:
        print(f"❌ Erreur lors de la création de bag-info.txt : {e}")

