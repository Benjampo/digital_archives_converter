import os
from helpers.to_snake_case import to_snake_case
from helpers.folders import count_files_and_folders
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    SpinnerColumn,
)
from rich import print
from config.ignore import text_files_to_ignore


def rename_files_and_folders(folder, selected_media_types):
    print("[bold cyan]Starting renaming files and folders[/bold cyan] :pencil2:")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
    ) as progress:
        total_files, total_folders = count_files_and_folders(
            folder, selected_media_types
        )
        total_items = total_files + total_folders
        rename_task = progress.add_task(
            "[bold blue]Renaming items...[/bold blue]", total=total_items
        )

        for root, dirs, files in os.walk(folder, topdown=False):
            # Rename files
            for file in files:
                if (
                    file == ".DS_Store"
                    or file.startswith(".")
                    or file in text_files_to_ignore
                ):  # Skip .DS_Store files and hidden files
                    continue
                new_name = to_snake_case(file)
                os.rename(os.path.join(root, file), os.path.join(root, new_name))
                progress.advance(rename_task)

            # Rename folders
            for dir in dirs:
                if dir == "VIDEO_TS" or file.startswith("."):  # Skip VIDEO_TS folders
                    progress.advance(rename_task)
                    continue
                new_name = to_snake_case(dir)
                os.rename(os.path.join(root, dir), os.path.join(root, new_name))
                progress.advance(rename_task)

        progress.update(rename_task, completed=total_items)
