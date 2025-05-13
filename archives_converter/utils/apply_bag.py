from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
import os
from helpers.bagit import create_bag_info, create_bagit_txt
import bagit
import csv
from datetime import datetime


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
            if os.path.exists(os.path.join(item_path, "bagit.txt")):
                bag = bagit.Bag(item_path)
                try:
                    if not bag.is_valid():
                        print(
                            f"[bold yellow]Bag at {item_path} is invalid. Updating manifest...[/bold yellow]"
                        )
                        bag.save(manifests=True)  # Recalculate and save the manifest
                    else:
                        print(
                            f"[bold green]Bag at {item_path} is valid. Skipping...[/bold green]"
                        )
                except Exception as e:
                    print(
                        f"[bold red]Error updating manifest for {item_path}: {e}[/bold red]"
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
                        details = "; ".join(
                            [
                                f"{type(d).__name__}: {d.path} (expected {d.expected}, found {d.found})"
                                if isinstance(d, bagit.ChecksumMismatch)
                                else f"{type(d).__name__}: {d.path}"
                                for d in e.details
                            ]
                        )
                        csv_writer.writerow([item_path, "❌", details])
                else:
                    print(
                        f"[bold red]No bagit.txt found at {item_path}. Skipping...[/bold red]"
                    )
                    csv_writer.writerow([item_path, "❌", "Missing bagit.txt"])
                progress.advance(task)

    print("[bold green]:heavy_check_mark: BagIt integrity check complete![/bold green]")
    print(f"[bold blue]Results saved to {csv_filepath}[/bold blue]")
