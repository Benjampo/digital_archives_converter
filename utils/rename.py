import os
from helpers.to_snake_case import to_snake_case
from helpers.folders import count_files_and_folders
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn

def rename_files(folder):
    print("[bold cyan]Starting renaming[/bold cyan] :pencil2:")

    with Progress(
        SpinnerColumn(spinner_name='clock'),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn()
    ) as progress:
        total_files, _ = count_files_and_folders(folder)
        rename_task = progress.add_task("[bold blue]Renaming files...[/bold blue]", total=total_files)

        for root, dirs, files in os.walk(folder):
            for file in files:
                if file == '.DS_Store':  # Skip .DS_Store files
                    continue
                new_name = to_snake_case(file)
                os.rename(os.path.join(root, file), os.path.join(root, new_name))
                progress.advance(rename_task)

        progress.update(rename_task, completed=total_files)