import os
from rich import print
import inquirer
import tkinter as tk
from tkinter import filedialog
from utils.convert import convert_folder
from utils.clone import clone_folder
from utils.rename import rename_files_and_folders

def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select Source Folder")
    root.destroy()
    return folder

def main():
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
                          choices=['Clone and convert directory', 'Clone directory', 'Rename directory', 'Exit'],
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
                                      ('DVD (VIDEO_TS)', 'dvd'),
                                      ('Audio files', 'audio'),
                                      ('Video files', 'video'),
                                      ('Image files', 'image'),
                                      ('Text files', 'text')
                                  ],
                                  default=['dvd', 'audio', 'video', 'image', 'text'])
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
            source_folder = select_folder()
            if not source_folder:
                print("[bold red]No folder selected. Please try again.[/bold red]")
                continue
            print(f"Selected source folder: [cyan]{source_folder}[/cyan]")
            clone_folder(source_folder)
            break
        elif action == 'Rename directory':
            rename_files_and_folders(source_folder)
            break

    print("[bold green]Thank you for using Archive Converter![/bold green]")

if __name__ == "__main__":
    main()