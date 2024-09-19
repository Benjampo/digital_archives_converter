import os
import subprocess
import shutil
from PIL import Image
import logging
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def delete_empty_folders(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"Deleted empty folder: {dir_path}")
            except Exception as e:
                print(f"Error deleting empty folder {dir_path}: {str(e)}")

def convert_folder(source_folder, destination_folder=None):
    # Use the source folder if destination folder is not provided
    if destination_folder is None:
        destination_folder = source_folder
        add_master_prefix = True
    else:
        add_master_prefix = False

    # Use the existing destination folder if it exists, otherwise clone the source folder
    if os.path.exists(destination_folder):
        print(f"Using existing destination folder: {destination_folder}")
    else:
        print(f"Cloning source folder to: {destination_folder}")
        shutil.copytree(source_folder, destination_folder)
        print(f"Cloned source folder to: {destination_folder}")

    # Count total files for progress bar
    total_files = sum([len(files) for _, _, files in os.walk(destination_folder)])
    
    with tqdm(total=total_files, desc="Converting files", unit="file") as pbar:
        # Walk through the cloned folder
        for root, dirs, files in os.walk(destination_folder):
            
            # Handle image files
            image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
            for img_file in image_files:
                input_path = os.path.join(root, img_file)
                output_path = os.path.splitext(input_path)[0] + '.tiff'
                if add_master_prefix:
                    output_path = os.path.join(root, 'Master_' + os.path.basename(output_path))
                try:
                    with Image.open(input_path) as img:
                        img.save(output_path, 'TIFF')
                    logging.info(f"Converted {img_file} to TIFF")
                    pbar.update(1)
                    os.remove(input_path)  # Remove the original image file
                except Exception as e:
                    print(f"Error converting {img_file} to TIFF: {str(e)}")
                
            # Handle audio files
            audio_files = [f for f in files if f.lower().endswith(('.mp3', '.aac', '.m4a', '.flac', '.ogg', '.m4p', '.aif', '.aiff'))]
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
                    pbar.update(1)
                    os.remove(input_path)  # Remove the original audio file
                except subprocess.CalledProcessError as e:
                    print(f"Error converting {audio_file} to WAV: {e.stderr}")
                
            # Handle classic video files
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
                    pbar.update(1)
                    os.remove(input_path)  # Remove the original video file
                except subprocess.CalledProcessError as e:
                    print(f"Error converting {video_file} to FFV1: {e.stderr}")

            if 'VIDEO_TS' in dirs:
                video_ts_path = os.path.join(root, 'VIDEO_TS')
                vob_files = sorted([f for f in os.listdir(video_ts_path) if f.endswith('.VOB')])
                if vob_files:
                    mkv_files = []
                    for vob_file in vob_files:
                        input_file = os.path.join(video_ts_path, vob_file)
                        output_file = os.path.join(root, f"{os.path.splitext(vob_file)[0]}.mkv")
                        
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
                            subprocess.run(ffmpeg_command, check=True, stderr=subprocess.PIPE, universal_newlines=True)
                            logging.info(f"Converted {vob_file} to {os.path.basename(output_file)}")
                            pbar.update(1)
                            mkv_files.append(output_file)
                        except subprocess.CalledProcessError as e:
                            print(f"Warning: FFmpeg encountered an error processing {vob_file}: {e.stderr}")
                            print("Attempting to continue processing...")
                
                    # Delete MKV files shorter than 5 seconds
                    for mkv_file in mkv_files[:]:
                        duration_command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', mkv_file]
                        try:
                            duration = float(subprocess.check_output(duration_command).decode('utf-8').strip())
                            if duration < 5:
                                os.remove(mkv_file)
                                mkv_files.remove(mkv_file)
                                print(f"Deleted {os.path.basename(mkv_file)} (duration: {duration:.2f}s)")
                        except subprocess.CalledProcessError as e:
                            print(f"Error checking duration of {os.path.basename(mkv_file)}: {e}")

                    # Merge remaining MKV files
                    if mkv_files:
                        merged_output = os.path.join(root, f"{os.path.basename(root)}.mkv")
                        concat_file = os.path.join(root, 'concat_list.txt')
                        with open(concat_file, 'w') as f:
                            for mkv_file in mkv_files:
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
                            logging.info(f"Merged MKV files into {os.path.basename(merged_output)}")
                            
                            # Delete individual MKV files and concat list
                            for mkv_file in mkv_files:
                                os.remove(mkv_file)
                            os.remove(concat_file)

                            # Delete VIDEO_TS folder after successful merge
                            try:
                                shutil.rmtree(video_ts_path)
                                logging.info(f"Deleted VIDEO_TS folder: {video_ts_path}")
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

    # After all conversions, delete empty folders
    logging.info("Deleting empty folders...")
    delete_empty_folders(destination_folder)

    logging.info(f"Conversion complete. Output folder: {destination_folder}")

# Example usage
convert_folder('/Users/benjaminporchet/Desktop/example_folder')
