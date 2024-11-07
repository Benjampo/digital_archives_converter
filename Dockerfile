# Use Python 3.12 slim base image
FROM python:3.12-slim-buster

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libreoffice \
    libimage-exiftool-perl \
    ghostscript \
    python3-opencv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available
EXPOSE 80

# Define environment variable
ENV NAME ArchiveConversionTool

# Run the application
CMD ["python", "archives_converter"]