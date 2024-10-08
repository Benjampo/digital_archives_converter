import os
import subprocess
import shutil
import concurrent.futures
import re
from rich import print

def convert_vob_to_mkv(input_file, output_file):
    # Check the duration of the VOB file
    duration_command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
    duration_output = subprocess.check_output(duration_command).decode('utf-8').strip()
    
    if duration_output == 'N/A':
        print(f"[bold orange]Warning:[/bold orange] Unable to determine duration for {input_file}. Skipping conversion.")
        return None
    
    try:
        duration = float(duration_output)
    except ValueError:
        print(f"[bold orange]Warning:[/bold orange] Invalid duration value '{duration_output}' for {input_file}. Skipping conversion.")
        return None
    
    if duration < 5:
        print(f"[bold orange]Skipping:[/bold orange] {os.path.basename(input_file)} (duration: {duration:.2f}s)")
        return None
    
    # FFmpeg command to convert each VOB file to MKV
    ffmpeg_command = [
        'ffmpeg',
        '-i', input_file,
        '-map_metadata', '0',
        '-c:v', 'ffv1',
        '-level', '3',
        '-coder', '1',
        '-context', '1',
        '-g', '1',
        '-slices', '24',
        '-slicecrc', '1',
        '-threads', '0',
        '-c:a', 'copy',
        '-c:s', 'copy',
        '-err_detect', 'ignore_err',
        '-fflags', '+genpts',
        '-max_interleave_delta', '0',           
        output_file
    ]
    try:
        subprocess.run(ffmpeg_command, timeout=1200, check=True, stderr=subprocess.PIPE, universal_newlines=True)
        print(f"[bold green]Converted file:[/bold green] {input_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"[bold orange]Warning:[/bold orange] FFmpeg encountered an error processing {os.path.basename(input_file)}: {e.stderr}")
        print("[bold yellow]Attempting to continue processing...[/bold yellow]")
        return None

def convert_to_mkv(video_ts_paths, output_folder):
    conversion_performed = False
    for video_ts_path in video_ts_paths:
        # Ensure we're looking inside the VIDEO_TS folder
        video_ts_folder = os.path.join(video_ts_path, 'VIDEO_TS')
        if not os.path.isdir(video_ts_folder):
            print(f"[bold yellow]Warning:[/bold yellow] VIDEO_TS folder not found in {video_ts_path}")
            continue

        # Sort VOB files numerically
        vob_files = sorted([f for f in os.listdir(video_ts_folder) if f.lower().endswith('.vob')],
                           key=lambda x: int(re.search(r'VTS_(\d+)_', x).group(1)) if re.search(r'VTS_(\d+)_', x) else 0)
        print(video_ts_folder)
        # Create a subfolder for intermediate and final outputs
        subfolder = os.path.join(output_folder, 'converting_videos')
        os.makedirs(subfolder, exist_ok=True)
                
        if vob_files:
            # Prepare conversion tasks
            conversion_tasks = []
            for vob_file in vob_files:
                input_file = os.path.join(video_ts_folder, vob_file)
                output_file = os.path.join(subfolder, f"{os.path.splitext(vob_file)[0]}.mkv")
                conversion_tasks.append((input_file, output_file))
            
            # Convert VOB files concurrently
            with concurrent.futures.ThreadPoolExecutor() as executor:
                mkv_files = list(filter(None, executor.map(lambda x: convert_vob_to_mkv(*x), conversion_tasks)))

            if mkv_files:
                if len(mkv_files) == 1:
                    # If there's only one MKV file, rename and move it
                    single_mkv = mkv_files[0]
                    final_output = os.path.join(output_folder, f"{os.path.basename(output_folder)}.mkv")
                    shutil.move(single_mkv, final_output)
                    shutil.rmtree(subfolder)
                    print(f"[bold green]Moved single MKV:[/bold green] {final_output}")
                    
                    # Delete VIDEO_TS folder after single file conversion
                    try:
                        shutil.rmtree(video_ts_folder)
                        print(f"[bold red]Deleted VIDEO_TS folder:[/bold red] {video_ts_folder}")
                    except PermissionError:
                        print(f"[bold orange]Warning:[/bold orange] Unable to delete {video_ts_folder} due to permission error. Skipping.")
                    except Exception as e:
                        print(f"[bold red]Error:[/bold red] Failed to delete {video_ts_folder}: {str(e)}")

                else:
                    # Merge multiple MKV files
                    merged_output = os.path.join(subfolder, f"{os.path.basename(output_folder)}_ffv1.mkv")
                    concat_file = os.path.join(subfolder, 'concat_list.txt')

                    def safe_sort_key(x):
                        match = re.search(r'VTS_(\d+)_', x)
                        return int(match.group(1)) if match else 0

                    with open(concat_file, 'w') as f:
                        for mkv_file in sorted(mkv_files, key=safe_sort_key):
                            f.write(f"file '{mkv_file}'\n")
                    
                    merge_command = [
                        'ffmpeg',
                        '-f', 'concat',
                        '-safe', '0',
                        '-i', concat_file,
                        '-map_metadata', '0',
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
                            shutil.rmtree(video_ts_folder)
                            print(f"[bold red]Deleted VIDEO_TS folder:[/bold red] {video_ts_folder}")
                        except PermissionError:
                            print(f"[bold yellow]Warning:[/bold yellow] Unable to delete {video_ts_folder} due to permission error. Skipping.")
                        except Exception as e:
                            print(f"[bold red]Error:[/bold red] Failed to delete {video_ts_folder}: {str(e)}")
                    
                    except subprocess.CalledProcessError as e:
                        print(f"Error merging MKV files: {e.stderr}")
                    conversion_performed = True
            else:
                # If no MKV files were created (e.g., all were too short), still try to delete VIDEO_TS
                try:
                    shutil.rmtree(video_ts_path)
                    conversion_performed = True
                    print(f"[bold green]Deleted VIDEO_TS folder:[/bold green] {video_ts_path}")
                except PermissionError:
                    print(f"[bold yellow]Warning:[/bold yellow] Unable to delete {video_ts_path} due to permission error. Skipping.")
                except Exception as e:
                    print(f"[bold red]Error:[/bold red] Failed to delete {video_ts_path}: {str(e)}")
                
    return conversion_performed
