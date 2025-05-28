import os
import subprocess
import shutil
import concurrent.futures
import re
from rich import print


def convert_vob_to_output(input_file, output_file, output_format):
    # Check the duration of the VOB file
    duration_command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        input_file,
    ]
    duration_output = subprocess.check_output(duration_command).decode("utf-8").strip()

    if duration_output == "N/A" or float(duration_output) < 5:
        return None

    # FFmpeg command to convert each VOB file to the desired format
    ffmpeg_command = [
        "ffmpeg",
        "-i",
        input_file,
        "-map_metadata",
        "0",
        "-err_detect",
        "ignore_err",
        "-fflags",
        "+genpts",
        "-max_interleave_delta",
        "0",
    ]

    if output_format == "mkv":
        ffmpeg_command.extend(
            [
                "-c:v",
                "ffv1",
                "-level",
                "3",
                "-coder",
                "1",
                "-context",
                "1",
                "-g",
                "1",
                "-slices",
                "24",
                "-slicecrc",
                "1",
                "-threads",
                "0",
                "-c:a",
                "flac",
                "-c:s",
                "copy",
            ]
        )
    elif output_format == "mp4":
        ffmpeg_command.extend(
            [
                "-c:v",
                "libx264",
                "-preset",
                "faster",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-c:s",
                "mov_text",
                "-threads",
                "0",
            ]
        )

    ffmpeg_command.append(output_file)

    try:
        print(f"[bold yellow]Converting file:[/bold yellow] {input_file}")
        subprocess.run(
            ffmpeg_command,
            timeout=1200,
            check=True,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        print(f"[bold green]Converted file:[/bold green] {input_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(
            f"[bold salmon1]Warning:[/bold salmon1] FFmpeg encountered an error processing {os.path.basename(input_file)}: {e.stderr}"
        )
        print("[bold yellow]Attempting to continue processing...[/bold yellow]")
        return None


def convert_dvd_to_format(video_ts_paths, output_folder, output_format):
    conversion_performed = False
    for video_ts_path in video_ts_paths:
        # Ensure we're looking inside the VIDEO_TS folder
        video_ts_folder = os.path.join(video_ts_path, "VIDEO_TS")
        if not os.path.isdir(video_ts_folder):
            print(
                f"[bold yellow]Warning:[/bold yellow] VIDEO_TS folder not found in {video_ts_path}"
            )
            continue

        # Sort VOB files numerically
        vob_files = sorted(
            [f for f in os.listdir(video_ts_folder) if f.lower().endswith(".vob")],
            key=lambda x: int(re.search(r"VTS_(\d+)_", x).group(1))
            if re.search(r"VTS_(\d+)_", x)
            else 0,
        )
        # Create a subfolder for intermediate and final outputs
        subfolder = os.path.join(output_folder, "converting_videos")
        os.makedirs(subfolder, exist_ok=True)

        if vob_files:
            # Prepare conversion tasks
            conversion_tasks = []
            for vob_file in vob_files:
                input_file = os.path.join(video_ts_folder, vob_file)
                extension = os.path.splitext(input_file)[1].lower().lstrip(".")
                output_file = (
                    os.path.splitext(input_file)[0] + f"_{extension}.{output_format}"
                )
                conversion_tasks.append((input_file, output_file, output_format))

            # Convert VOB files concurrently
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=os.cpu_count() - 1
            ) as executor:
                converted_files = list(
                    filter(
                        None,
                        executor.map(
                            lambda x: convert_vob_to_output(*x), conversion_tasks
                        ),
                    )
                )

            if converted_files:
                if len(converted_files) == 1:
                    # If there's only one converted file, rename and move it
                    single_file = converted_files[0]
                    final_output = os.path.join(
                        output_folder,
                        f"{os.path.basename(output_folder)}.{output_format}",
                    )
                    shutil.move(single_file, final_output)
                    shutil.rmtree(subfolder)
                    print(
                        f"[bold green]Moved single {output_format.upper()} file:[/bold green] {final_output}"
                    )
                else:
                    # Merge multiple converted files
                    merged_output = os.path.join(
                        subfolder, f"{os.path.basename(output_folder)}.{output_format}"
                    )
                    concat_file = os.path.join(subfolder, "concat_list.txt")

                    def safe_sort_key(x):
                        match = re.search(r"VTS_(\d+)_", x)
                        return int(match.group(1)) if match else 0

                    with open(concat_file, "w") as f:
                        for mkv_file in sorted(converted_files, key=safe_sort_key):
                            f.write(f"file '{mkv_file}'\n")

                    merge_command = [
                        "ffmpeg",
                        "-f",
                        "concat",
                        "-safe",
                        "0",
                        "-i",
                        concat_file,
                        "-map_metadata",
                        "0",
                        "-c",
                        "copy",
                        "-threads",
                        "0",
                        merged_output,
                    ]

                    try:
                        subprocess.run(
                            merge_command,
                            check=True,
                            stderr=subprocess.PIPE,
                            universal_newlines=True,
                        )

                        # Move the merged file to the root folder
                        output_suffix = (
                            "ffv1" if output_format == "mkv" else output_format
                        )
                        final_output = os.path.join(
                            output_folder,
                            f"{os.path.basename(output_folder)}_{output_suffix}.{output_format}",
                        )
                        shutil.move(merged_output, final_output)

                        # Delete individual MKV files and concat list
                        for mkv_file in converted_files:
                            os.remove(mkv_file)
                        os.remove(concat_file)

                        # Delete subfolder after successful merge
                        shutil.rmtree(subfolder)

                        # Delete VIDEO_TS folder after successful merge
                        try:
                            shutil.rmtree(video_ts_folder)
                            print(
                                f"[bold red]Deleted VIDEO_TS folder:[/bold red] {video_ts_folder}"
                            )
                        except PermissionError:
                            print(
                                f"[bold yellow]Warning:[/bold yellow] Unable to delete {video_ts_folder} due to permission error. Skipping."
                            )
                        except Exception as e:
                            print(
                                f"[bold red]Error:[/bold red] Failed to delete {video_ts_folder}: {str(e)}"
                            )

                    except subprocess.CalledProcessError as e:
                        print(
                            f"Error merging {output_format.upper()} files: {e.stderr}"
                        )
                conversion_performed = True
            else:
                # If no converted files were created (e.g., all were too short), still try to delete VIDEO_TS
                try:
                    shutil.rmtree(video_ts_path)
                    conversion_performed = True
                    print(
                        f"[bold green]Deleted VIDEO_TS folder:[/bold green] {video_ts_path}"
                    )
                except PermissionError:
                    print(
                        f"[bold yellow]Warning:[/bold yellow] Unable to delete {video_ts_path} due to permission error. Skipping."
                    )
                except Exception as e:
                    print(
                        f"[bold red]Error:[/bold red] Failed to delete {video_ts_path}: {str(e)}"
                    )

    return conversion_performed


def convert_dvd_to_mkv(video_ts_paths, output_folder):
    return convert_dvd_to_format(video_ts_paths, output_folder, "mkv")


def convert_dvd_to_mp4(video_ts_paths, output_folder):
    return convert_dvd_to_format(video_ts_paths, output_folder, "mp4")
