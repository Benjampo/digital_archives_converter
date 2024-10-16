import os
import logging

def delete_empty_folders(folder, progress=None, task=None):
    for root, dirs, files in os.walk(folder, topdown=False):
        if not files and not os.listdir(root):
            try:
                os.rmdir(root)
                if progress and task:
                    progress.advance(task)
                logging.info(f"Deleted empty folder: {root}")
            except OSError as e:
                logging.error(f"Error deleting folder {root}: {e}")
