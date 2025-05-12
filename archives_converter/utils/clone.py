import os
from helpers.folders import copy_folder_with_progress
from rich import print
import shutil
from helpers.to_snake_case import to_snake_case
from helpers.folders import should_copy_file
from helpers.name_identifier import predict_name_based_on_extension


def clone_folder(
    source_folder, clone_type, selected_media_types, destination_folder=None
):
    print("[bold cyan]Starting cloning[/bold cyan] :cd:")

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

    for root, dirs, files in os.walk(destination_folder):
        for file in files:
            if file == "bagit.txt":
                data_dir = os.path.join(root, "data")
                if os.path.exists(data_dir):
                    for data_root, data_dirs, data_files in os.walk(data_dir):
                        for data_file in data_files:
                            destination_files = True

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            new_name_file = to_snake_case(file)
            os.rename(os.path.join(root, file), os.path.join(root, new_name_file))
            if file == ".DS_Store":
                continue

            src_file = os.path.join(root, new_name_file)
            relative_path = to_snake_case(os.path.relpath(src_file, source_folder))

            dst_dir = os.path.join(destination_folder, os.path.dirname(relative_path))
            if destination_files:
                dst_dir = os.path.join(
                    destination_folder, os.path.dirname(relative_path), "data"
                )

            dst_file = os.path.join(dst_dir, os.path.basename(relative_path))

            if not os.path.exists(
                predict_name_based_on_extension(dst_file, clone_type)
            ):
                if should_copy_file(file, selected_media_types):
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    shutil.copy2(src_file, dst_file)
            else:
                print(f"File already exists: {relative_path}")
