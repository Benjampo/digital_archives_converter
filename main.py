import os
from rich import print
import inquirer
import tkinter as tk
from tkinter import filedialog
from convert import convert_folder

def main():
    print("[bold green]Welcome to Archive Converter![/bold green]")
    
    questions = [
        inquirer.List('action',
                      message="What do you want to do today?",
                      choices=['Clone and convert directory', 'Clone directory', 'Rename directory'],
                      default=['Clone and convert directory']),
    ]
    action = inquirer.prompt(questions)

    # Use tkinter file dialog to pick source folder
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    source_folder = filedialog.askdirectory(title="Select Source Folder")
        
    if not source_folder:
        print("[bold red]No folder selected. Exiting.[/bold red]")
        return
   
    print(f"Selected source folder: [cyan]{source_folder}[/cyan]")
    # Handle different actions
    if action == 'Rename directory':
        print(f"Renaming directory...")
    if action == 'Clone and convert directory':
        convert_folder(source_folder)
    elif action == 'Clone directory':
        print("Cloning source directory...")

if __name__ == "__main__":
    main()