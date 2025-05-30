from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
import os
from helpers.bagit import create_bag_info, create_bagit_txt
import bagit
import csv
from datetime import datetime
from helpers.bagit import update_bag_info


def apply_bag(destination_folder):
    print("[bold yellow]Creating BagIt structure...[/bold yellow]")
    items = [
        item
        for item in os.listdir(destination_folder)
        if os.path.isdir(os.path.join(destination_folder, item)) and item != ".DS_Store"
    ]
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task(
            "[bold blue]Creating BagIt structure...", total=len(items)
        )
        for item in items:
            item_path = os.path.join(destination_folder, item)

            # Ensure item_path is a directory
            if not os.path.isdir(item_path):
                print(
                    f"[bold red]Error: {item_path} is not a directory. Skipping...[/bold red]"
                )
                continue

            for root, dirs, files in os.walk(item_path):
                for file in files:
                    if file == ".DS_Store":
                        os.remove(os.path.join(root, file))

            if os.path.exists(os.path.join(item_path, "bagit.txt")):
                bag = bagit.Bag(item_path)

                try:
                    if not bag.is_valid():
                        print(
                            f"[bold yellow]Bag at {item_path} is invalid. Updating manifest...[/bold yellow]"
                        )
                        # Gather all data file paths relative to item_path
                        relative_file_paths = []
                        for root, dirs, files in os.walk(item_path):
                            for file in files:
                                if file == ".DS_Store":
                                    continue
                                # Exclude tag files (bagit.txt, bag-info.txt, manifest-*.txt, etc.)
                                if file.endswith(".txt") and (
                                    file.startswith("bagit")
                                    or file.startswith("bag-info")
                                    or file.startswith("manifest-")
                                    or file.startswith("tagmanifest-")
                                ):
                                    continue
                                abs_path = os.path.join(root, file)
                                rel_path = os.path.relpath(abs_path, item_path)
                                relative_file_paths.append(rel_path)
                        update_bag_info(item_path, relative_file_paths)
                    else:
                        print(
                            f"[bold green]Bag at {item_path} is valid. Skipping...[/bold green]"
                        )
                except Exception as e:
                    print(
                        f"[bold red]Error updating manifest for {item_path}: {e}[/bold red]"
                    )
                continue

            # Ensure item_path is still a directory before creating a BagIt structure
            if not os.path.isdir(item_path):
                print(
                    f"[bold red]Error: {item_path} is not a directory after processing. Skipping...[/bold red]"
                )
                continue

            bagit.make_bag(item_path, checksums=["sha256"])
            create_bagit_txt(item_path)
            create_bag_info(item_path)

            bag = bagit.Bag(item_path)
            bag.save(manifests=True)

            progress.advance(task)

    print("[bold green]:heavy_check_mark: BagIt structure created![/bold green]")


def check_bag_integrity(destination_folder):
    print("[bold yellow]Checking BagIt integrity...[/bold yellow]")
    items = [
        item
        for item in os.listdir(destination_folder)
        if os.path.isdir(os.path.join(destination_folder, item)) and item != ".DS_Store"
    ]

    all_valid = True  # Track overall validity

    # Prepare CSV file
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    csv_filename = f"bag_integrity_{date_str}.csv"
    csv_filepath = os.path.join(destination_folder, csv_filename)
    with open(csv_filepath, mode="w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Path", "Status", "Details"])

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task(
                "[bold blue]Checking BagIt integrity...", total=len(items)
            )
            for item in items:
                item_path = os.path.join(destination_folder, item)
                if os.path.exists(os.path.join(item_path, "bagit.txt")):
                    bag = bagit.Bag(item_path)
                    try:
                        bag.validate()
                        print(f"[bold green]Bag at {item_path} is valid.[/bold green]")
                        csv_writer.writerow([item_path, "✅", "Valid Bag"])
                    except bagit.BagValidationError as e:
                        print(f"[bold red]Bag at {item_path} is invalid![/bold red]")
                        if hasattr(e, "details") and e.details:
                            details = "; ".join(
                                [
                                    f"{type(d).__name__}: {d.path} (expected {getattr(d, 'expected', '?')}, found {getattr(d, 'found', '?')})"
                                    if isinstance(d, bagit.ChecksumMismatch)
                                    else f"{type(d).__name__}: {getattr(d, 'path', '?')}"
                                    for d in e.details
                                ]
                            )
                        else:
                            details = str(
                                e
                            )  # Fallback to exception message if no details
                        csv_writer.writerow([item_path, "❌", details])
                        all_valid = False
                else:
                    print(
                        f"[bold red]No bagit.txt found at {item_path}. Skipping...[/bold red]"
                    )
                    csv_writer.writerow([item_path, "❌", "Missing bagit.txt"])
                    all_valid = False  # Mark as invalid
                progress.advance(task)

    print("[bold green]:heavy_check_mark: BagIt integrity check complete![/bold green]")
    print(f"[bold blue]Results saved to {csv_filepath}[/bold blue]")
    return all_valid
