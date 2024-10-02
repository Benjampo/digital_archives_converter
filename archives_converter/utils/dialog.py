import inquirer
from utils.convert import convert_folder
from utils.clone import clone_folder
from utils.rename import rename_files_and_folders
from helpers.metadata import create_metadata_files
import tkinter as tk
from tkinter import filedialog
from rich import print
from helpers.metadata import metadata_to_html_table
def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select Source Folder")
    root.destroy()
    return folder

def select_metadata_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select Metadata file", filetypes=[("YAML files", "*.yaml")])
    root.destroy()
    return file_path

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
    This program is designed to convert video files from VOB to MKV format.
    It utilizes the power of FFmpeg for efficient conversion and offers
    options to clone, rename, or convert directories.
    [/yellow]
    """
    print(welcome_message)
    
    while True:
        questions = [
            inquirer.List('action',
                          message="What do you want to do today?",
                          choices=['Clone and convert directory', 'Clone directory', 'Rename directory', 'visualize metadata', 'Exit'],
                          default=['Clone and convert directory']),
        ]
        action = inquirer.prompt(questions)['action']

        if action == 'Exit':
            break

        if action == 'Clone and convert directory':
            conversion_options = [
                inquirer.Checkbox('media_types',
                                  message="Select media types to convert:",
                                  choices=[
                                      ('Audio files', 'audio'),
                                      ('Video files', 'video'),
                                      ('Image files', 'image'),
                                      ('Text files', 'text'),
                                      ('DVD (VIDEO_TS)', 'dvd'),
                                  ],
                                  default=['audio', 'video', 'image', 'text'])
            ]
            selected_media_types = inquirer.prompt(conversion_options)['media_types']
            source_folder = select_folder()
            if not source_folder:
                print("[bold red]No folder selected. Please try again.[/bold red]")
                continue
            print(f"Selected source folder: [cyan]{source_folder}[/cyan]")
            convert_folder(source_folder, selected_media_types)
            break
        elif action == 'Clone directory':
            conversion_options = [
                inquirer.Checkbox('media_types',
                                  message="Select media types to clone:",
                                  choices=[
                                      ('Audio files', 'audio'),
                                      ('Video files', 'video'),
                                      ('Image files', 'image'),
                                      ('Text files', 'text'),
                                      ('DVD (VIDEO_TS)', 'dvd'),
                                  ],
                                  default=['audio', 'video', 'image', 'text', 'dvd'])
            ]
            selected_media_types = inquirer.prompt(conversion_options)['media_types']
            source_folder = select_folder()
            if not source_folder:
                print("[bold red]No folder selected. Please try again.[/bold red]")
                continue
            print(f"Selected source folder: [cyan]{source_folder}[/cyan]")
            clone_folder(source_folder, selected_media_types)
            break
        elif action == 'Rename directory':
            rename_files_and_folders(source_folder)
            break
        elif action == 'visualize metadata':
            metadata_file_path = select_metadata_file()
            if not metadata_file_path:
                print("[bold red]No file selected. Please try again.[/bold red]")
                continue
            print(f"Selected metadata file: [cyan]{metadata_file_path}[/cyan]")
            metadata_to_html_table(metadata_file_path)
            break

    print("[bold green]Thank you for using Archive Converter![/bold green]")