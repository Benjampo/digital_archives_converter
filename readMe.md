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

## Installation

1. Install Homebrew:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install Python:
   ```
   brew install python
   ```

3. Install FFmpeg:
   ```
   brew install ffmpeg
   ```

## Setup

1. Create a virtual environment:
   ```
   python -m venv env
   ```

2. Activate the virtual environment:
   ```
   source env/bin/activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Ensure your virtual environment is activated. If you haven't created one yet, follow these steps:

- Create a virtual environment:
     ```
     python -m venv env
     ```
   - Activate the virtual environment:
     - On macOS and Linux:
       ```
       source env/bin/activate
       ```
     - On Windows:
       ```
       .\env\Scripts\activate
       ```

2. Run the script:
   ```
   python test.py
   ```

   Or use the provided shell script:
   ```
   ./run_script.sh
   ```

3. The script will process the files in the specified source folder and output the converted files to the destination folder.

4. Progress will be displayed in the console, along with logging information.

## Configuration

You can modify the source and destination folders in the `test.py` file:
