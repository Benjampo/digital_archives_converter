import os
from helpers.folders import copy_folder_with_progress
from rich import print
import shutil
from helpers.to_snake_case import to_snake_case
from helpers.folders import should_copy_file
from helpers.name_identifier import predict_name_based_on_extension
from config.formats import text_files_to_ignore


def clone_folder(
    source_folder, clone_type, selected_media_types, destination_folder=None
):
    print("[bold cyan]Starting cloning[/bold cyan] :cd:")

    # If no destination folder is provided, determine it based on clone_type
    if destination_folder is None:
        base_name = os.path.basename(source_folder)

        if base_name.startswith("SIP_"):
            base_name = base_name[4:]

        if clone_type == "AIP":
            destination_folder = os.path.join(
                os.path.dirname(source_folder), f"AIP_{base_name}"
            )
        elif clone_type == "DIP":
            destination_folder = os.path.join(
                os.path.dirname(source_folder), f"DIP_{base_name}"
            )
        elif clone_type == "clone":
            destination_folder = os.path.join(
                os.path.dirname(source_folder), f"CLONE_{base_name}"
            )
        else:
            raise ValueError(f"Invalid clone type: {clone_type}")

    # If destination exists, only clone changes; otherwise, copy the whole folder
    if os.path.exists(destination_folder):
        cloning_changes_to_folder(
            source_folder, destination_folder, selected_media_types, clone_type
        )
    else:
        print("[bold yellow]Cloning source folder...[/bold yellow]")
        copy_folder_with_progress(
            source_folder, destination_folder, selected_media_types
        )
        print("[bold green]Cloned source folder[/bold green]")

    return destination_folder


def cloning_changes_to_folder(
    source_folder, destination_folder, selected_media_types, clone_type
):
    print("[bold yellow]Cloning changes to folder...[/bold yellow]")
    destination_files = False  # Flag to check if destination has BagIt 'data' files

    bagit_data_dir = None  # Will hold path to BagIt data dir in source if found

    # --- Check if destination is a BagIt folder by looking for 'bagit.txt' ---
    for root, dirs, files in os.walk(destination_folder):
        for file in files:
            if file == "bagit.txt":
                data_dir = os.path.join(root, "data")
                if os.path.exists(data_dir):
                    # If 'data' dir exists, set flag to True
                    for data_root, data_dirs, data_files in os.walk(data_dir):
                        for data_file in data_files:
                            destination_files = True

    # --- Check if source is a BagIt folder by looking for 'bagit.txt' ---
    for root, dirs, files in os.walk(source_folder):
        if "bagit.txt" in files:
            bagit_data_dir = os.path.join(root, "data")
            break  # Only need the first occurrence

    # --- If source is BagIt, copy new files from its data directory ---
    if bagit_data_dir and os.path.exists(bagit_data_dir):
        for data_root, data_dirs, data_files in os.walk(bagit_data_dir):
            for data_file in data_files:
                # Skip copying bag-info.txt and other tag files if they exist in destination
                if data_file in text_files_to_ignore:
                    dst_check = os.path.join(
                        destination_folder,
                        os.path.relpath(
                            os.path.join(data_root, data_file), source_folder
                        ),
                    )
                    if os.path.exists(dst_check):
                        continue  # Do not overwrite tag files
                src_file = os.path.join(data_root, data_file)

                # Compute relative path and convert to snake_case
                relative_path = to_snake_case(os.path.relpath(src_file, source_folder))

                # Decide destination directory based on BagIt structure and file type
                dst_dir = (
                    os.path.join(data_root, os.path.dirname(relative_path))
                    if destination_files
                    and "data" not in src_file
                    and data_file not in text_files_to_ignore
                    else os.path.join(
                        destination_folder, os.path.dirname(relative_path)
                    )
                )

                # Final destination file path
                dst_file = os.path.join(dst_dir, os.path.basename(relative_path))

                # Only copy if file does not already exist in destination (with extension prediction)
                if not os.path.exists(
                    predict_name_based_on_extension(dst_file, clone_type)
                ):
                    if should_copy_file(data_file, selected_media_types):
                        # Ensure destination directory exists
                        os.makedirs(os.path.dirname(dst_dir), exist_ok=True)
                        shutil.copy2(src_file, dst_file)  # Copy file with metadata
                else:
                    print(
                        f"[bold salmon1]File already exists in data: {relative_path}[/bold salmon1]"
                    )

        # TODO: Update bag-info.txt in source and destination if files were added

    # --- Walk through all files in the source folder to copy new/changed files ---
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file == ".DS_Store":
                continue  # Skip macOS system files

            # Skip copying bag-info.txt and other tag files if they exist in destination
            if file in text_files_to_ignore:
                dst_check = os.path.join(
                    destination_folder,
                    os.path.relpath(os.path.join(root, file), source_folder),
                )
                if os.path.exists(dst_check):
                    continue  # Do not overwrite tag files

            src_file = os.path.join(root, file)

            # Compute relative path and convert to snake_case
            relative_path = to_snake_case(os.path.relpath(src_file, source_folder))

            # Decide destination directory based on BagIt structure and file type
            dst_dir = (
                os.path.join(destination_folder, os.path.dirname(relative_path), "data")
                if destination_files
                and "data" not in src_file
                and file not in text_files_to_ignore
                else os.path.join(destination_folder, os.path.dirname(relative_path))
            )

            # Final destination file path
            dst_file = os.path.join(dst_dir, os.path.basename(relative_path))

            # Only copy if file does not already exist in destination (with extension prediction)
            if not os.path.exists(
                predict_name_based_on_extension(dst_file, clone_type)
            ):
                if should_copy_file(file, selected_media_types):
                    # Ensure destination directory exists
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    shutil.copy2(src_file, dst_file)  # Copy file with metadata
            else:
                print(
                    f"[bold orange]File already exists: {relative_path}[/bold orange]"
                )
