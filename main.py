import os
from rich import print
import inquirer
import tkinter as tk
from tkinter import filedialog
from utils.convert import convert_folder
from utils.clone import clone_folder
from utils.rename import rename_files


def main():
    print("[bold green]Welcome to Archive Converter![/bold green]")
    
    questions = [
        inquirer.List('action',
                      message="What do you want to do today?",
                      choices=['Clone and convert directory', 'Clone directory', 'Rename directory'],
                      default=['Clone and convert directory']),
    ]
    action = inquirer.prompt(questions)['action']

    root = tk.Tk()
    root.withdraw()  # Hide the main window

    source_folder = filedialog.askdirectory(title="Select Source Folder")
        
    if not source_folder:
        print("[bold red]No folder selected. Exiting.[/bold red]")
        return
   
    print(f"Selected source folder: [cyan]{source_folder}[/cyan]")

    if action == 'Clone and convert directory':
        convert_folder(source_folder)
    elif action == 'Clone directory':
        clone_folder(source_folder)
    elif action == 'Rename directory':
        rename_files(source_folder)

if __name__ == "__main__":
    main()