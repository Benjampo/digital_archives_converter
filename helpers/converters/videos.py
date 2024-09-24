import os
import subprocess
import logging

def convert_videos(files, root):
    video_files = [f for f in files if f.lower().endswith(('.mp4', '.avi', '.mov', '.flv'))]
    for file in files:
        input_path = os.path.join(root, file)
        if not os.path.exists(input_path):
            print(f"Warning: File not found: {input_path}")
            continue

        for video_file in video_files:
            if video_file == file:
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
                    subprocess.run(ffmpeg_command, check=True, stderr=subprocess.PIPE, universal_newlines=True,  errors='ignore')
                    try:
                        os.remove(input_path)  # Remove the original video file
                    except FileNotFoundError:
                        print(f"Warning: Original file not found for removal: {input_path}")
                        continue
                except subprocess.CalledProcessError as e:
                    print(f"Error converting {video_file} to FFV1: {e.stderr}")