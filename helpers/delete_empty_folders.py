import os
import logging

def delete_empty_folders(folder, progress=None, task=None):
    for root, dirs, files in os.walk(folder, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                os.rmdir(dir_path)
                if progress and task:
                    progress.advance(task)
            except OSError:
                pass