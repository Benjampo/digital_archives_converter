import os
import subprocess
import logging
from helpers.metadata import extract_metadata, append_metadata

def convert_wav(files, root):
    return convert_audio(files, root, 'wav', 'pcm_s16le', 44100)

def convert_mp3(files, root):
    return convert_audio(files, root, 'mp3', 'libmp3lame', 44100)

def convert_audio(files, root, target_format, codec, sample_rate):
    metadata_file = os.path.join(root, 'metadata.json')
    audio_files = [f for f in files if f.lower().endswith(('.wav', '.aac', '.m4a', '.flac', '.ogg', '.aif', '.aiff'))]
    conversion_performed = False
    for audio_file in audio_files:
        input_path = os.path.join(root, audio_file)
        output_path = os.path.splitext(input_path)[0] + f'_{target_format}.{target_format}'
        metadata_file = os.path.join(os.path.dirname(input_path), 'metadata.json')
        try:
            # Get original file's timestamps
            original_stat = os.stat(input_path)
            
            # Extract metadata before conversion
            metadata = extract_metadata(input_path)
            
            ffmpeg_command = [
                'ffmpeg',
                '-i', input_path,
                '-map_metadata', '0',
                '-acodec', codec,
                '-ar', str(sample_rate),
                output_path
            ]
         
            subprocess.run(ffmpeg_command, check=True, timeout=300, stderr=subprocess.PIPE, universal_newlines=True)
            
            # Set the new file's timestamps to match the original
            os.utime(output_path, (original_stat.st_atime, original_stat.st_mtime))
            
            append_metadata(metadata, metadata_file, output_path)
            
            os.remove(input_path)  # Remove the original audio file
            conversion_performed = True
        except subprocess.CalledProcessError as e:
            logging.error(f"Error converting {audio_file} to {target_format.upper()}: {e.stderr}")
        except OSError as e:
            logging.error(f"OS error occurred while processing {audio_file}: {e}")
    return conversion_performed


