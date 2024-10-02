import hashlib
import os
import shutil


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
            for file in files:
                if file != "manifest-md5.txt":
                    file_path = os.path.join(root, file)
                    md5_hash = generate_md5(file_path)
                    relative_path = os.path.relpath(file_path, folder)
                    manifest.write(f"{md5_hash}  {relative_path}\n")

def create_bagit_txt(folder):
    bagit_path = os.path.join(folder, "bagit.txt")
    with open(bagit_path, "w") as bagit_file:
        bagit_file.write("BagIt-Version: 0.97\n")
        bagit_file.write("Tag-File-Character-Encoding: UTF-8\n")

