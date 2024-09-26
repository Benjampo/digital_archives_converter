# Archive Conversion Tool

This tool converts various media files (images, audio, video) to archival formats.

## Features

- Converts images to TIFF format
- Converts audio files to WAV format
- Converts video files to FFV1 format
- Handles DVD (VIDEO_TS) conversion
- Deletes empty folders after conversion (it will delete menus and stuff)
- Provides logging and progress bar for better visibility of the conversion process

## Requirements

- Python 3.6+
- Pillow
- tqdm
- FFmpeg (must be installed separately and available in system PATH)
- LibreOffice (for document conversion)

## Installation

### macOS

1. Install Homebrew:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install Python, FFmpeg, and LibreOffice:
   ```
   brew install python ffmpeg libreoffice
   ```

### Linux (Ubuntu/Debian)

1. Update package list and install Python, FFmpeg, and LibreOffice:
   ```
   sudo apt update
   sudo apt install python3 python3-pip ffmpeg libreoffice
   ```

### Windows

1. Install Python from the [official website](https://www.python.org/downloads/).
2. Install FFmpeg:
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Add FFmpeg to your system PATH
3. Install LibreOffice from the [official website](https://www.libreoffice.org/download/download/).

## Setup

1. Clone the repository or download the source code.

2. Create a virtual environment:
   ```
   python3 -m venv venv  # On macOS and Linux
   python -m venv venv   # On Windows
   ```

3. Activate the virtual environment:
   - macOS and Linux:
     ```
     source venv/bin/activate
     ```
   - Windows:
     ```
     venv\Scripts\activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Activate the virtual environment (if not already activated).

2. Run the script:
   ```
   python archives_converter
   ```

3. The script will process the files in the specified source folder and output the converted files to the destination folder.

4. Progress will be displayed in the console, along with logging information.
