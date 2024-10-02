import os
import subprocess
import logging
from helpers.metadata import extract_metadata, append_metadata

def convert_audio(files, root):
    metadata_file = os.path.join(root, 'metadata.txt')
    audio_files = [f for f in files if f.lower().endswith(('.mp3', '.aac', '.m4a', '.flac', '.ogg', '.aif', '.aiff'))]
    for audio_file in audio_files:
        input_path = os.path.join(root, audio_file)
        output_path = os.path.splitext(input_path)[0] + '_wav.wav'
        try:
            # Get original file's timestamps
            original_stat = os.stat(input_path)
            
            # Extract metadata before conversion
            metadata = extract_metadata(input_path)
            
            ffmpeg_command = [
                'ffmpeg',
                '-i', input_path,
                '-map_metadata', '0',
                '-acodec', 'pcm_s16le',
                '-ar', '44100',
                output_path
            ]
         
            subprocess.run(ffmpeg_command, check=True, timeout=300, stderr=subprocess.PIPE, universal_newlines=True)
            
            # Set the new file's timestamps to match the original
            os.utime(output_path, (original_stat.st_atime, original_stat.st_mtime))
            
            # Append metadata to the metadata.txt file
            append_metadata(metadata, metadata_file, input_path)
            
            os.remove(input_path)  # Remove the original audio file
        except subprocess.CalledProcessError as e:
            logging.error(f"Error converting {audio_file} to WAV: {e.stderr}")
        except OSError as e:
            logging.error(f"OS error occurred while processing {audio_file}: {e}")