import os
import subprocess
import logging

def convert_to_audio(audio_files):
    for audio_file in audio_files:
        input_path = os.path.join(root, audio_file)
        output_path = os.path.splitext(input_path)[0] + '.wav'
        try:
            ffmpeg_command = [
                'ffmpeg',
                '-i', input_path,
                '-acodec', 'pcm_s16le',
                '-ar', '44100',
                output_path
            ]
            subprocess.run(ffmpeg_command, check=True, stderr=subprocess.PIPE, universal_newlines=True)
            logging.info(f"Converted {audio_file} to WAV")
            os.remove(input_path)  # Remove the original audio file
        except subprocess.CalledProcessError as e:
            print(f"Error converting {audio_file} to WAV: {e.stderr}")
    progress_bar['value'] += 1
    root.update()