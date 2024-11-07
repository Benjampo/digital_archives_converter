# Makefile for Archive Conversion Tool

# Python command (use python3 on macOS and Linux, python on Windows)
PYTHON := python3.12
ifeq ($(OS),Windows_NT)
    PYTHON := python
endif

# Virtual environment directory
VENV := venv

# Activate virtual environment command
ifeq ($(OS),Windows_NT)
    VENV_ACTIVATE := $(VENV)\Scripts\activate
else
    VENV_ACTIVATE := . $(VENV)/bin/activate
endif

.PHONY: all prereq venv install run clean reset

all: prereq venv install
	@echo "Setup complete. Run 'make run' to start the Archive Conversion Tool."

prereq:
	@echo "Checking and installing prerequisites..."
ifeq ($(OS),Windows_NT)
	@echo "Please install Python, FFmpeg, LibreOffice, and unoconv manually on Windows."
else
    ifeq ($(shell uname),Darwin)
		@echo "Checking for Homebrew..."
		@which brew > /dev/null || (echo "Installing Homebrew..." && /bin/bash -c "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)")
		@echo "Checking for Python..."
		@which python3.12 > /dev/null || (echo "Installing Python..." && brew install python@3.12)
		@echo "Checking for tkinter..."
		@which python3.12-tk > /dev/null || (echo "Installing tkinter..." && brew install python-tk@3.12)
		@echo "Checking for FFmpeg..."
		@which ffmpeg > /dev/null || (echo "Installing FFmpeg..." && brew install ffmpeg)
		@echo "Checking for LibreOffice..."
		@[ -f "/Applications/LibreOffice.app/Contents/MacOS/soffice" ] || (echo "Installing LibreOffice..." && brew install --cask libreoffice)
		@echo "Checking for ExifTool..."
		@which exiftool > /dev/null || (echo "Installing ExifTool..." && brew install exiftool)
    else
		@echo "Checking for Python 3.12..."
		@which python3.12 > /dev/null || (echo "Installing Python 3.12..." && sudo apt-get update && sudo apt-get install -y software-properties-common && sudo add-apt-repository -y ppa:deadsnakes/ppa && sudo apt-get update && sudo apt-get install -y python3.12 python3.12-venv python3.12-dev)
		@echo "Checking for Python 3.12 tkinter..."
		@dpkg -l | grep -q python3.12-tk || (echo "Installing Python 3.12 tkinter..." && sudo apt-get update && sudo apt-get install -y python3.12-tk)
		@echo "Checking for FFmpeg..."
		@which ffmpeg > /dev/null || (echo "Installing FFmpeg..." && sudo apt-get update && sudo apt-get install -y ffmpeg)
		@echo "Checking for LibreOffice..."
		@which libreoffice > /dev/null || (echo "Installing LibreOffice..." && sudo apt-get update && sudo apt-get install -y libreoffice)
		@echo "Checking for ExifTool..."
		@which exiftool > /dev/null || (echo "Installing ExifTool..." && sudo apt-get update && sudo apt-get install -y libimage-exiftool-perl)
    endif
endif
	@echo "Prerequisites check complete."

venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created."

install: venv
	@echo "Installing required packages..."
	$(VENV_ACTIVATE) && pip install -r requirements.txt
	@echo "Required packages installed."

run: venv
	@echo "Starting Archive Conversion Tool..."
	$(VENV_ACTIVATE) && trap 'deactivate' EXIT && $(PYTHON) archives_converter

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	@echo "Cleanup complete."

reset:
	@echo "Resetting environment..."
	@-pkill -f "$(PYTHON) archives_converter" 2>/dev/null || true
	@-deactivate 2>/dev/null || true
	@make clean
	@make all
	@echo "Environment reset complete."
