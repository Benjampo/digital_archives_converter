import os
import subprocess
import logging

def convert_audio(files, root):
    audio_files = [f for f in files if f.lower().endswith(('.mp3', '.aac', '.m4a', '.flac', '.ogg', '.aif', '.aiff'))]
    for audio_file in audio_files:
        input_path = os.path.join(root, audio_file)
        output_path = os.path.splitext(input_path)[0] + '_wav.wav'
        try:
            ffmpeg_command = [
                'ffmpeg',
                '-i', input_path,
                '-acodec', 'pcm_s16le',
                '-ar', '44100',
                output_path
            ]
         
            subprocess.run(ffmpeg_command, check=True, timeout=300, stderr=subprocess.PIPE, universal_newlines=True)
            os.remove(input_path)  # Remove the original audio file
        except subprocess.CalledProcessError as e:
            logging.error(f"Error converting {audio_file} to WAV: {e.stderr}")  # Use logging for errors