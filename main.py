import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from convert import convert_folder
import logging

def select_source_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        source_folder_entry.delete(0, tk.END)
        source_folder_entry.insert(0, folder_selected)

def select_destination_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        destination_folder_entry.delete(0, tk.END)
        destination_folder_entry.insert(0, folder_selected)

def start_conversion():
    source_folder = source_folder_entry.get()
    destination_folder = destination_folder_entry.get()
    
    logging.info(f"Start conversion clicked. Source folder: {source_folder}, Destination folder: {destination_folder}")
    
    if not source_folder:
        messagebox.showerror("Error", "Please select a source folder.")
        return
    if not destination_folder:
        destination_folder = None
    
    # Hide the input fields and buttons
    hide_inputs()
    
    try:
        convert_folder(source_folder, destination_folder, progress_bar)
        messagebox.showinfo("Success", "Conversion completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def hide_inputs():
    source_folder_label.grid_remove()
    source_folder_entry.grid_remove()
    source_folder_button.grid_remove()
    destination_folder_label.grid_remove()
    destination_folder_entry.grid_remove()
    destination_folder_button.grid_remove()
    start_button.grid_remove()

def show_inputs():
    source_folder_label.grid()
    source_folder_entry.grid()
    source_folder_button.grid()
    destination_folder_label.grid()
    destination_folder_entry.grid()
    destination_folder_button.grid()
    start_button.grid()

# Create the main window
root = tk.Tk()
root.title("File Converter")
root.geometry("600x250")
root.configure(bg="#f0f0f0")

# Define Shadn styles
label_style = {"font": ("Helvetica", 12, "bold"), "bg": "#2c3e50", "fg": "#ecf0f1"}
entry_style = {"font": ("Helvetica", 12), "bg": "#34495e", "fg": "#ecf0f1", "relief": "flat", "bd": 2}
button_style = {"font": ("Helvetica", 12, "bold"), "bg": "#e74c3c", "fg": "#ecf0f1", "activebackground": "#c0392b", "relief": "flat", "bd": 3}

# Source folder selection
source_folder_label = tk.Label(root, text="Source Folder:", **label_style)
source_folder_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
source_folder_entry = tk.Entry(root, width=50, **entry_style)
source_folder_entry.grid(row=0, column=1, padx=10, pady=10)
source_folder_button = tk.Button(root, text="Browse...", command=select_source_folder, **button_style)
source_folder_button.grid(row=0, column=2, padx=10, pady=10)

# Destination folder selection
destination_folder_label = tk.Label(root, text="Destination Folder:", **label_style)
destination_folder_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
destination_folder_entry = tk.Entry(root, width=50, **entry_style)
destination_folder_entry.grid(row=1, column=1, padx=10, pady=10)
destination_folder_button = tk.Button(root, text="Browse...", command=select_destination_folder, **button_style)
destination_folder_button.grid(row=1, column=2, padx=10, pady=10)

# Start conversion button
start_button = tk.Button(root, text="Start Conversion", command=start_conversion, **button_style)
start_button.grid(row=2, column=0, columnspan=3, pady=20)

# Progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress_bar.grid(row=3, column=0, columnspan=3, pady=10)

# Run the application
root.mainloop()