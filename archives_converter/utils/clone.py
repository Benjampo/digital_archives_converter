import os
from helpers.folders import copy_folder_with_progress
from rich import print
import shutil
from helpers.to_snake_case import to_snake_case
from helpers.folders import should_copy_file
from helpers.name_identifier import predict_name_based_on_extension
from config.ignore import text_files_to_ignore
from helpers.bagit import update_bag_info


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
    destination_files = False

    bagit_data_dir = None
    added_files = []

    # Check if the destination folder is a BagIt folder by looking for bagit.txt
    for root, dirs, files in os.walk(destination_folder):
        for file in files:
            if file == "bagit.txt":
                data_dir = os.path.join(root, "data")
                bag_info_dest_path = os.path.join(root)
                if os.path.exists(data_dir):
                    for data_root, data_dirs, data_files in os.walk(data_dir):
                        for data_file in data_files:
                            destination_files = True

    # Check if the source folder is a BagIt folder by looking for bagit.txt
    for root, dirs, files in os.walk(source_folder):
        if "bagit.txt" in files:
            bagit_data_dir = os.path.join(root, "data")
            bag_info_src_path = os.path.join(root)
            break

    # If source is a BagIt folder, copy new files from its data directory
    if bagit_data_dir and os.path.exists(bagit_data_dir):
        for data_root, data_dirs, data_files in os.walk(bagit_data_dir):
            for data_file in data_files:
                src_file = os.path.join(data_root, data_file)

                relative_path = to_snake_case(os.path.relpath(src_file, source_folder))

                dst_dir = (
                    os.path.join(data_root, os.path.dirname(relative_path))
                    if destination_files
                    and "data" not in src_file
                    and data_file not in text_files_to_ignore
                    else os.path.join(
                        destination_folder, os.path.dirname(relative_path)
                    )
                )

                dst_file = os.path.join(dst_dir, os.path.basename(relative_path))

                # Only copy if file does not already exist in destination
                if not os.path.exists(
                    predict_name_based_on_extension(dst_file, clone_type)
                ):
                    if should_copy_file(data_file, selected_media_types):
                        os.makedirs(os.path.dirname(dst_dir), exist_ok=True)
                        shutil.copy2(src_file, dst_file)
                        added_files.append(relative_path)  # Track added file
                else:
                    print(
                        f"[bold salmon1]File already exists in data: {relative_path}[/bold salmon1]"
                    )

        # Update bag-info.txt in source and destination if files were added
        if added_files:
            if os.path.exists(bag_info_src_path):
                update_bag_info(bag_info_src_path, added_files)
            if "bag_info_dest_path" in locals() and os.path.exists(bag_info_dest_path):
                update_bag_info(bag_info_dest_path, added_files)

    # Walk through all files in the source folder to copy new/changed files
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            new_name_file = to_snake_case(file)

            if file == ".DS_Store":
                continue

            src_file = os.path.join(root, file)

            # Apply snake_case to the relative path for the destination
            relative_path = to_snake_case(os.path.relpath(src_file, source_folder))
            print("relative_path:", relative_path)
            dst_dir = (
                os.path.join(destination_folder, os.path.dirname(relative_path), "data")
                if destination_files
                and "data" not in src_file
                and file not in text_files_to_ignore
                else os.path.join(destination_folder, os.path.dirname(relative_path))
            )

            dst_file = os.path.join(dst_dir, os.path.basename(relative_path))

            if not os.path.exists(
                predict_name_based_on_extension(dst_file, clone_type)
            ):
                if should_copy_file(file, selected_media_types):
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    shutil.copy2(src_file, dst_file)
            else:
                print(
                    f"[bold orange]File already exists: {relative_path}[/bold orange]"
                )
