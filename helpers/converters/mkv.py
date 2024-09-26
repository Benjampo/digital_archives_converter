import os
import subprocess
import shutil
import logging
import concurrent.futures
import re

def convert_to_mkv(video_ts_paths, output_folder):
    for video_ts_path in video_ts_paths:
        video_ts_path = os.path.join(output_folder, 'VIDEO_TS')
        # Sort VOB files numerically
        vob_files = sorted([f for f in os.listdir(video_ts_path) if f.lower().endswith('.vob')],
                           key=lambda x: int(re.search(r'VTS_(\d+)_', x).group(1)))
        
        # Create a subfolder for intermediate and final outputs
        subfolder = os.path.join(output_folder, 'converted_videos')
        os.makedirs(subfolder, exist_ok=True)
        
        if vob_files:
            mkv_files = []
            
            def process_vob(vob_file):
                input_file = os.path.join(video_ts_path, vob_file)
                output_file = os.path.join(subfolder, f"{os.path.splitext(vob_file)[0]}.mkv")
                
                # Check the duration of the VOB file
                duration_command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
                duration_output = subprocess.check_output(duration_command).decode('utf-8').strip()
                
                if duration_output == 'N/A':
                    print(f"Warning: Unable to determine duration for {input_file}. Skipping conversion.")
                    return None
                
                try:
                    duration = float(duration_output)
                except ValueError:
                    print(f"Warning: Invalid duration value '{duration_output}' for {input_file}. Skipping conversion.")
                    return None
                
                if duration < 5:
                    print(f"Skipping {vob_file} (duration: {duration:.2f}s)")
                    return None
                
                # FFmpeg command to convert each VOB file to MKV
                ffmpeg_command = [
                    'ffmpeg',
                    '-i', input_file,
                    '-c:v', 'ffv1',
                    '-crf', '23',
                    '-c:a', 'aac',
                    '-c:s', 'copy',
                    '-err_detect', 'ignore_err',
                    '-fflags', '+genpts',
                    '-max_interleave_delta', '0',
                    output_file
                ]
                try:
                    subprocess.run(ffmpeg_command, timeout=1200, check=True, stderr=subprocess.PIPE, universal_newlines=True)
                    return output_file
                except subprocess.CalledProcessError as e:
                    print(f"Warning: FFmpeg encountered an error processing {vob_file}: {e.stderr}")
                    print("Attempting to continue processing...")
                    return None

            # Use ThreadPoolExecutor to process VOB files in parallel
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_vob = {executor.submit(process_vob, vob_file): vob_file for vob_file in vob_files}
                for future in concurrent.futures.as_completed(future_to_vob):
                    result = future.result()
                    if result:
                        mkv_files.append(result)

            # Merge remaining MKV files
            if mkv_files:
                merged_output = os.path.join(subfolder, f"{os.path.basename(output_folder)}.mkv")
                concat_file = os.path.join(subfolder, 'concat_list.txt')
                with open(concat_file, 'w') as f:
                    for mkv_file in sorted(mkv_files, key=lambda x: int(re.search(r'VTS_(\d+)_', x).group(1))):
                        f.write(f"file '{mkv_file}'\n")
                
                merge_command = [
                    'ffmpeg',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', concat_file,
                    '-c', 'copy',
                    merged_output
                ]
                
                try:
                    subprocess.run(merge_command, check=True, stderr=subprocess.PIPE, universal_newlines=True)
                    
                    # Move the merged MKV file to the root folder
                    final_output = os.path.join(output_folder, f"{os.path.basename(output_folder)}.mkv")
                    shutil.move(merged_output, final_output)
                    
                    # Delete individual MKV files and concat list
                    for mkv_file in mkv_files:
                        os.remove(mkv_file)
                    os.remove(concat_file)
                    
                    # Delete subfolder after successful merge
                    shutil.rmtree(subfolder)
                    
                    # Delete VIDEO_TS folder after successful merge
                    try:
                        shutil.rmtree(video_ts_path)
                    except PermissionError:
                        logging.warning(f"Unable to delete {video_ts_path} due to permission error. Skipping.")
                    except Exception as e:
                        logging.error(f"Error deleting {video_ts_path}: {str(e)}")
                
                except subprocess.CalledProcessError as e:
                    print(f"Error merging MKV files: {e.stderr}")
            else:
                # If no MKV files were created (e.g., all were too short), still try to delete VIDEO_TS
                try:
                    shutil.rmtree(video_ts_path)
                    logging.info(f"Deleted VIDEO_TS folder: {video_ts_path}")
                except PermissionError:
                    logging.warning(f"Unable to delete {video_ts_path} due to permission error. Skipping.")
                except Exception as e:
                    logging.error(f"Error deleting {video_ts_path}: {str(e)}")
