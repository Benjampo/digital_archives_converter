import os
import logging

def delete_empty_folders(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"Deleted empty folder")
            except Exception as e:
                print(f"Error deleting empty folder {dir_path}: {str(e)}")