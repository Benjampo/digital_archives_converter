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

.PHONY: all prereq venv install run clean

all: prereq venv install

prereq:
ifeq ($(OS),Windows_NT)
	@echo "Please install Python, FFmpeg, and LibreOffice manually on Windows."
else
    ifeq ($(shell uname),Darwin)
		brew install python ffmpeg libreoffice
    else
		sudo apt update
		sudo apt install -y python3 python3-pip ffmpeg libreoffice
    endif
endif

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(VENV_ACTIVATE) && pip install -r requirements.txt

run: venv
	$(VENV_ACTIVATE) && $(PYTHON) archives_converter.py

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
