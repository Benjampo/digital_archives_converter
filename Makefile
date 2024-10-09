# Makefile for Archive Conversion Tool

# Python command (use python3 on macOS and Linux, python on Windows)
PYTHON := python3
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

prereq:
ifeq ($(OS),Windows_NT)
	@echo "Please install Python, FFmpeg, and LibreOffice manually on Windows."
else
    ifeq ($(shell uname),Darwin)
		@which python3 > /dev/null || brew install python
		@which ffmpeg > /dev/null || brew install ffmpeg
		@which libreoffice > /dev/null || brew install --cask libreoffice
		@which exiftool > /dev/null || brew install exiftool
    else
		@which python3 > /dev/null || (sudo apt update && sudo apt install -y python3 python3-pip)
		@which ffmpeg > /dev/null || (sudo apt update && sudo apt install -y ffmpeg)
		@which libreoffice > /dev/null || (sudo apt update && sudo apt install -y libreoffice)
		@which exiftool > /dev/null || (sudo apt update && sudo apt install -y libimage-exiftool-perl)
    endif
endif

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(VENV_ACTIVATE) && pip install -r requirements.txt

run: venv
	$(VENV_ACTIVATE) && trap 'deactivate' EXIT && $(PYTHON) archives_converter

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

reset:
	@echo "Resetting environment..."
	@-pkill -f "$(PYTHON) archives_converter" 2>/dev/null || true
	@-deactivate 2>/dev/null || true
	@make clean
	@make all
