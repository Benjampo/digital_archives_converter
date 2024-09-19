import os
import subprocess
import logging

def convert_to_videos(source_folder, destination_folder):
    video_files = [f for f in files if f.lower().endswith(('.mp4', '.avi', '.mov', '.wmv', '.flv'))]
    for video_file in video_files:
        input_path = os.path.join(root, video_file)
            output_path = os.path.splitext(input_path)[0] + '_ffv1.mkv'
        try:
            ffmpeg_command = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', 'ffv1',
                '-level', '3',
                '-c:a', 'copy',
                '-c:s', 'copy',
                output_path
            ]
            subprocess.run(ffmpeg_command, check=True, stderr=subprocess.PIPE, universal_newlines=True)
            logging.info(f"Converted {video_file} to FFV1")
                os.remove(input_path)  # Remove the original video file
            except subprocess.CalledProcessError as e:
                print(f"Error converting {video_file} to FFV1: {e.stderr}")
        progress_bar['value'] += 1
        root.update()