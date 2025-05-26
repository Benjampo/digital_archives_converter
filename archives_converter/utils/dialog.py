import inquirer
from utils.convert import convert_folder
from utils.clone import clone_folder
from utils.rename import rename_files_and_folders
import tkinter as tk
from tkinter import filedialog
from rich import print
from .apply_bag import apply_bag, check_bag_integrity


def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder = None
    try:
        folder = filedialog.askdirectory(title="Select Source Folder")
    finally:
        root.destroy()
        tk._default_root = None  # Ensure the default root is cleared
    return folder


def dialog():
    welcome_message = """
    [bold cyan]
     ██████╗██╗     ███████╗██████╗ 
    ██╔════╝██║     ██╔════╝██╔══██╗
    ██║     ██║     ███████╗██████╔╝
    ██║     ██║     ╚════██║██╔══██╗
    ╚██████╗███████╗███████║██║  ██║
     ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝
    [/bold cyan]
    [bold green]
    ╔═══════════════════════════════════╗
    ║    WELCOME TO ARCHIVE CONVERTER   ║
    ╚═══════════════════════════════════╝
    [/bold green]
    [yellow]
    This script is designed to convert media files from various formats to a standardized format.
    It can clone, rename, or convert directories.
    [/yellow]
    """
    thank_you_message = """
        [bold cyan]
         ████████╗██╗  ██╗ █████╗ ███╗   ██╗██╗  ██╗███████╗
        ╚══██╔══╝██║  ██║██╔══██╗████╗  ██║██║ ██╔╝██╔════╝
           ██║   ███████║███████║██╔██╗ ██║█████╔╝ ███████╗
           ██║   ██╔══██║██╔══██║██║╚██╗██║██╔═██╗ ╚════██║
           ██║   ██║  ██║██║  ██║██║ ╚████║██║  ██╗███████║
           ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
        [/bold cyan]
        [bold green]
        ╔═════════════════════════════════════════════╗
        ║ THANK YOU FOR USING THE ARCHIVE CONVERTER!  ║
        ╚═════════════════════════════════════════════╝
        [/bold green]
        [yellow]
        Re-launch the script to convert another folder.
        [/yellow]
        """
    print(welcome_message)
    try:
        while True:
            # Ensure any lingering Tkinter root windows are destroyed before showing the menu again
            if hasattr(tk, "_default_root") and tk._default_root is not None:
                try:
                    tk._default_root.destroy()
                except Exception:
                    pass
                tk._default_root = None

            questions = [
                inquirer.List(
                    "action",
                    message="What do you want to do today?",
                    choices=[
                        "Clone and convert directory",
                        "apply Bagit format",
                        "Check Bag integrity",
                        "Clone directory",
                        "Rename directory",
                        "Exit",
                    ],
                    default="Clone and convert directory",
                ),
            ]
            action = inquirer.prompt(questions)["action"]

            if action == "Exit":
                print(thank_you_message)
                break

            if action == "Clone and convert directory":
                convert_type_options = [
                    inquirer.List(
                        "convert_type",
                        message="Select convert type:",
                        choices=["AIP", "DIP"],
                        default="AIP",
                    )
                ]
                convert_type = inquirer.prompt(convert_type_options)["convert_type"]
                conversion_options = [
                    inquirer.Checkbox(
                        "media_types",
                        message="Select media types to convert:",
                        choices=[
                            ("Audio files", "audio"),
                            ("Video files", "video"),
                            ("Image files", "image"),
                            ("Text files", "text"),
                            ("DVD (VIDEO_TS)", "dvd"),
                        ],
                        default=["audio", "video", "image", "text"],
                    )
                ]
                selected_media_types = inquirer.prompt(conversion_options)[
                    "media_types"
                ]
                source_folder = select_folder()
                if not source_folder:
                    print("[bold red]No folder selected. Please try again.[/bold red]")
                    continue
                print(f"Selected source folder: [cyan]{source_folder}[/cyan]")
                convert_folder(source_folder, convert_type, selected_media_types)
                continue
            elif action == "Clone directory":
                conversion_options = [
                    inquirer.Checkbox(
                        "media_types",
                        message="Select media types to clone:",
                        choices=[
                            ("Audio files", "audio"),
                            ("Video files", "video"),
                            ("Image files", "image"),
                            ("Text files", "text"),
                            ("DVD (VIDEO_TS)", "dvd"),
                        ],
                        default=["audio", "video", "image", "text", "dvd"],
                    )
                ]
                selected_media_types = inquirer.prompt(conversion_options)[
                    "media_types"
                ]
                source_folder = select_folder()
                if not source_folder:
                    print("[bold red]No folder selected. Please try again.[/bold red]")
                    continue
                print(f"Selected source folder: [cyan]{source_folder}[/cyan]")
                clone_folder(source_folder, "clone", selected_media_types)
                continue
            elif action == "Rename directory":
                source_folder = select_folder()
                if not source_folder:
                    print("[bold red]No folder selected. Please try again.[/bold red]")
                    continue
                rename_files_and_folders(source_folder)
                continue
            elif action == "apply Bagit format":
                source_folder = select_folder()
                if not source_folder:
                    print("[bold red]No folder selected. Please try again.[/bold red]")
                    continue
                apply_bag(source_folder)
                continue
            elif action == "Check Bag integrity":
                source_folder = select_folder()
                if not source_folder:
                    print("[bold red]No folder selected. Please try again.[/bold red]")
                    continue
                check_bag_integrity(source_folder)
                continue

    except Exception as e:
        print(f"[bold red]An error occurred: {e}[/bold red]")
        print(thank_you_message)
