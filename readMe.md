# Archive Conversion Tool

This tool converts various media files (images, audio, video) to archival formats. It also clones and renames directories.

## Features

- Converts images to TIFF format
- Converts audio files to WAV format
- Converts video files to FFV1 format
- Converts documents to PDF/A2-b
- Handles DVD (VIDEO_TS) conversion
- Deletes empty folders after conversion (it will delete menus and stuff)

## Requirements

- [Python 3.6+](https://www.python.org/): The script is written in Python and uses features available in Python 3.6 and later.
- [FFmpeg](https://www.ffmpeg.org/): Used for audio and video conversion tasks.
- [LibreOffice](https://www.libreoffice.org/): Required for document conversion to PDF/A2-b format.
- [ExifTool](https://exiftool.org/): Required for metadata extraction and embedding.

## Installation

### With Makefile (recommended)

```
make
```

## Usage

```
make run
```

## Manual installation

#### macOS

1. Install Homebrew:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install Python, FFmpeg, and LibreOffice:
   ```
   brew install python ffmpeg libreoffice exiftool
   ```

#### Linux (Ubuntu/Debian)

1. Update package list and install Python, FFmpeg, and LibreOffice:
   ```
   sudo apt update
   sudo apt install python3 python3-pip ffmpeg libreoffice libimage-exiftool-perl
   ```

#### Windows

1. Install Python from the [official website](https://www.python.org/downloads/).
2. Install FFmpeg:
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Add FFmpeg to your system PATH
3. Install LibreOffice from the [official website](https://www.libreoffice.org/download/download/).
4. Install ExifTool:
   - Download from [exiftool.org](https://exiftool.org/install.html)
   - Add ExifTool to your system PATH

#### Setup

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.