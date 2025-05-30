import os
import subprocess
import shutil
# from helpers.metadata import extract_metadata, append_metadata


def convert_ffv1(files, root):
    return convert_video(files, root, "_ffv1.mkv", "ffv1")


def convert_mp4(files, root):
    return convert_video(files, root, "_mp4.mp4", "libx264")


def convert_video(files, root, output_suffix, video_codec):
    video_files = [
        f for f in files if f.lower().endswith((".mp4", ".avi", ".mov", ".flv", ".mkv"))
    ]
    # metadata_file = os.path.join(root, "metadata.json")
    conversion_performed = False
    for file in files:
        input_path = os.path.join(root, file)
        if not os.path.exists(input_path):
            continue

        # Skip files that are already converted
        if file.lower().endswith(output_suffix):
            continue

        for video_file in video_files:
            if video_file == file:
                extension = os.path.splitext(input_path)[1].lower().lstrip(".")
                output_path = (
                    os.path.splitext(input_path)[0]
                    + f"_{extension}{output_suffix[-4:]}"
                )
                try:
                    # Store original file metadata
                    original_stat = os.stat(input_path)

                    # Extract metadata before conversion
                    # metadata = extract_metadata(input_path)

                    ffmpeg_command = [
                        "ffmpeg",
                        "-i",
                        input_path,
                        "-map_metadata",
                        "0",
                        "-c:v",
                        video_codec,
                        "-c:a",
                        "aac",
                        "-ar",
                        "44100",
                        "-pix_fmt",
                        "yuv420p",
                        "-movflags",
                        "+faststart",
                        "-sn",
                    ]

                    if video_codec == "libx264":
                        ffmpeg_command.extend(
                            [
                                "-preset",
                                "medium",
                                "-crf",
                                "23",
                                "-profile:v",
                                "main",
                                "-level",
                                "3.0",
                            ]
                        )
                    elif video_codec == "ffv1":
                        ffmpeg_command.extend(["-level", "3"])

                    ffmpeg_command.append(output_path)

                    subprocess.run(
                        ffmpeg_command,
                        timeout=600,
                        check=True,
                        stderr=subprocess.PIPE,
                        universal_newlines=True,
                        errors="ignore",
                    )

                    # Copy metadata to the new file
                    shutil.copystat(input_path, output_path)

                    # Manually set creation and modification times
                    os.utime(
                        output_path, (original_stat.st_atime, original_stat.st_mtime)
                    )

                    # append_metadata(metadata, metadata_file, output_path)

                    try:
                        os.remove(input_path)  # Remove the original video file
                        conversion_performed = True
                    except FileNotFoundError:
                        print(
                            f"Warning: Original file not found for removal: {input_path}"
                        )
                        continue
                except subprocess.CalledProcessError as e:
                    print(f"Error converting {video_file} to {video_codec}: {e.stderr}")
    return conversion_performed
