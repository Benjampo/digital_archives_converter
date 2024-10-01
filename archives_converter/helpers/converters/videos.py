import os
import subprocess
import shutil


def convert_videos(files, root):
    video_files = [f for f in files if f.lower().endswith(('.mp4', '.avi', '.mov', '.flv'))]
    for file in files:
        input_path = os.path.join(root, file)
        if not os.path.exists(input_path):
            continue

        # Skip files that are already converted
        if file.lower().endswith('_ffv1.mkv'):
            print(f"[bold orange]Skipping:[/bold orange] {file}")
            continue

        for video_file in video_files:
            if video_file == file:
                output_path = os.path.splitext(input_path)[0] + '_ffv1.mkv'
                try:
                    # Store original file metadata
                    original_stat = os.stat(input_path)

                    ffmpeg_command = [
                        'ffmpeg',
                        '-i', input_path,
                        '-map_metadata', '0',
                        '-c:v', 'ffv1',
                        '-level', '3',
                        '-c:a', 'copy',
                        '-sn',  # Disable subtitle streams
                        output_path
                    ]
                    subprocess.run(ffmpeg_command, timeout=600, check=True, stderr=subprocess.PIPE, universal_newlines=True, errors='ignore')
                    
                    # Copy metadata to the new file
                    shutil.copystat(input_path, output_path)
                    
                    # Manually set creation and modification times
                    os.utime(output_path, (original_stat.st_atime, original_stat.st_mtime))

                    try:
                        os.remove(input_path)  # Remove the original video file
                    except FileNotFoundError:
                        print(f"Warning: Original file not found for removal: {input_path}")
                        continue
                except subprocess.CalledProcessError as e:
                    print(f"Error converting {video_file} to FFV1: {e.stderr}")