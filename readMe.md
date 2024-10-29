# Archive Conversion Tool

This tool converts various media files (images, audio, video) to archival formats. It also clones and renames directories.

## Features

- Converts images to TIFF format (AIP) or JPG format (DIP)
- Converts audio files to WAV format (AIP) or MP3 format (DIP)
- Converts video files to FFV1 format (AIP) or MP4 format (DIP)
- Converts documents to PDF/A2-b
- Handles DVD (VIDEO_TS) conversion
- Deletes empty folders after conversion
- Creates BagIt structure
- Generates metadata files and HTML summary

## Requirements

- [Python 3.12+](https://www.python.org/): The script is written in Python and uses features available in Python 3.12 and later.
- [FFmpeg](https://www.ffmpeg.org/): Used for audio and video conversion tasks.
- [LibreOffice](https://www.libreoffice.org/): Required for document conversion to PDF/A2-b format.
- [ExifTool](https://exiftool.org/): Required for metadata extraction and embedding.
- [unoconv](https://github.com/dagwieers/unoconv): Required for converting Microsoft Office files.

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

### macOS

1. Install Homebrew:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install required packages:
   ```
   brew install python@3.12 python-tk@3.12 ffmpeg libreoffice exiftool unoconv
   ```

### Linux (Ubuntu/Debian)

1. Update package list and install required packages:
   ```
   sudo apt update
   sudo apt install software-properties-common
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt update
   sudo apt install python3.12 python3.12-venv python3.12-dev python3.12-tk ffmpeg libreoffice libimage-exiftool-perl unoconv
   ```

### Windows

1. Install Python 3.12 from the [official website](https://www.python.org/downloads/).
2. Install FFmpeg:
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Add FFmpeg to your system PATH
3. Install LibreOffice from the [official website](https://www.libreoffice.org/download/download/).
4. Install ExifTool:
   - Download from [exiftool.org](https://exiftool.org/install.html)
   - Add ExifTool to your system PATH
5. Install unoconv:
   - Follow the instructions for Windows installation on the [unoconv GitHub page](https://github.com/unoconv/unoconv)

### Setup

1. Clone the repository or download the source code.

2. Create a virtual environment:
   ```
   python3.12 -m venv venv  # On macOS and Linux
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


## Tips

- If you have issues running the script 2 times in a row (keyboard stuck). Go to action menu `cmd + shift + p` and select `Terminal: Focus on terminal`
