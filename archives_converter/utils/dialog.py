import inquirer
from utils.convert import convert_folder
from utils.clone import clone_folder
from utils.rename import rename_files_and_folders
import tkinter as tk
from tkinter import filedialog
from rich import print
from .apply_bag import apply_bag, check_bag_integrity
import sys
import termios

# Save the original terminal settings at module load
try:
    if sys.stdin.isatty():
        _original_term_settings = termios.tcgetattr(sys.stdin.fileno())
    else:
        _original_term_settings = None
except Exception:
    _original_term_settings = None


def reset_terminal():
    """
    Restore the terminal to its original settings if possible.
    """
    if sys.stdin.isatty() and _original_term_settings is not None:
        try:
            termios.tcsetattr(
                sys.stdin.fileno(), termios.TCSADRAIN, _original_term_settings
            )
        except Exception:
            pass


def select_folder():
    # Save terminal state before using tkinter
    if sys.stdin.isatty():
        try:
            saved_settings = termios.tcgetattr(sys.stdin.fileno())
        except Exception:
            saved_settings = None
    else:
        saved_settings = None
    root = tk.Tk()
    root.withdraw()
    folder = None
    try:
        folder = filedialog.askdirectory(title="Select Source Folder")
    finally:
        root.destroy()
        tk._default_root = None  # Ensure the default root is cleared
        # Restore terminal state after tkinter
        if sys.stdin.isatty() and saved_settings is not None:
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, saved_settings)
            except Exception:
                pass
        reset_terminal()
    return folder


def select_format_type():
    convert_type_options = [
        inquirer.List(
            "convert_type",
            message="Select convert type:",
            choices=["AIP", "DIP"],
            default="AIP",
        )
    ]
    reset_terminal()
    convert_type = inquirer.prompt(convert_type_options)["convert_type"]
    reset_terminal()
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
    reset_terminal()
    selected_media_types = inquirer.prompt(conversion_options)["media_types"]
    reset_terminal()
    source_folder = select_folder()
    if not source_folder:
        print("[bold red]No folder selected. Please try again.[/bold red]")
    print(f"Selected source folder: [cyan]{source_folder}[/cyan]")
    return source_folder, convert_type, selected_media_types


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

            questions = (
                inquirer.List(
                    "action",
                    message="What do you want to do today?",
                    choices=[
                        "Clone, update, convert and bag",
                        "Clone/update and convert directory",
                        "apply Bagit format",
                        "Check Bag integrity",
                        "Clone directory",
                        "Rename directory",
                        "Exit",
                    ],
                    default="Clone, update, convert and bag",
                ),
            )

            reset_terminal()
            action = inquirer.prompt(questions)["action"]
            reset_terminal()

            if action == "Exit":
                print(thank_you_message)
                break

            if action == "Clone and convert directory":
                source_folder, convert_type, selected_media_types = select_format_type()
                convert_folder(source_folder, convert_type, selected_media_types)
                continue
            elif action == "Clone, update, convert and bag":
                source_folder, convert_type, selected_media_types = select_format_type()
                check_bag_integrity(source_folder)
                convert_folder(source_folder, convert_type, selected_media_types)
                apply_bag(source_folder)
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
                reset_terminal()
                selected_media_types = inquirer.prompt(conversion_options)[
                    "media_types"
                ]
                reset_terminal()
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
