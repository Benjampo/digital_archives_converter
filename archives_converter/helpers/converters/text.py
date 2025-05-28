import os
import subprocess
import time
import shutil
# from helpers.metadata import extract_metadata, append_metadata


def convert_pdfa(files, root):
    metadata_file = os.path.join(root, "metadata.json")
    conversion_performed = False
    for file in files:
        if file.lower() in [
            "concat_list.txt",
            "metadata.json",
            "bagit.txt",
            "bag-info.txt",
            "manifest-sha256.txt",
            "tagmanifest-sha256.txt",
        ]:
            return conversion_performed

        input_path = os.path.join(root, file)
        extension = os.path.splitext(input_path)[1].lower().lstrip(".")
        output_path = os.path.splitext(input_path)[0] + f"_{extension}.pdf"

        if file.lower().endswith(".pdf"):
            conversion_performed = (
                convert_pdf_to_pdfa(input_path, output_path, metadata_file)
                or conversion_performed
            )
        elif file.lower().endswith((".txt", ".doc", ".docx", ".rtf", ".odt")):
            conversion_performed = (
                convert_to_pdf(input_path, output_path, metadata_file)
                or conversion_performed
            )

        original_file = output_path.replace(".pdf", ".pdf_original")
        if os.path.exists(original_file):
            os.remove(original_file)

    return conversion_performed


def convert_to_pdf(input_path, output_path, metadata_file):
    try:
        # Kill any lingering soffice.bin processes before starting unoconv
        subprocess.run(["pkill", "-f", "soffice.bin"], check=False, capture_output=True)

        try:
            subprocess.run(
                ["unoconv", "--listener"],
                timeout=30,
                check=False,
                capture_output=True,
            )
            time.sleep(5)
        except subprocess.TimeoutExpired:
            pass

        unoconv_command = [
            "unoconv",
            "-f",
            "pdf",
            "-eSelectPdfVersion=2",
            "-ePDFACompliance=2",
            "-o",
            output_path,
            input_path,
        ]
        subprocess.run(
            unoconv_command,
            timeout=100,
            check=True,
            capture_output=True,
            text=True,
        )

        original_stat = os.stat(input_path)

        exiftool_command = [
            "exiftool",
            "-tagsFromFile",
            input_path,
            "-all:all",
            output_path,
        ]
        try:
            subprocess.run(
                exiftool_command, timeout=60, check=True, capture_output=True, text=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Exiftool command failed for {input_path}: {e.stderr.strip()}")
            raise

        shutil.chown(output_path, original_stat.st_uid, original_stat.st_gid)
        os.chmod(output_path, original_stat.st_mode)
        os.utime(output_path, (original_stat.st_atime, original_stat.st_mtime))

        os.remove(input_path)
        return True
    except Exception as e:
        print(f"Unexpected error converting {input_path}: {str(e)}")
    return False


def convert_pdf_to_pdfa(input_path, output_path, metadata_file):
    try:
        original_stat = os.stat(input_path)

        timeout = 300
        gs_command = [
            "gs",
            "-dPDFA=2",
            "-dBATCH",
            "-dNOPAUSE",
            "-sColorConversionStrategy=UseDeviceIndependentColor",
            "-sProcessColorModel=DeviceCMYK",
            "-sDEVICE=pdfwrite",
            "-dPDFACompatibilityPolicy=1",
            "-dOverwritePDFMark=true",
            f"-sOutputFile={output_path}",
            input_path,
        ]

        subprocess.run(
            gs_command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True,
        )

        exiftool_command = [
            "exiftool",
            "-tagsFromFile",
            input_path,
            "-all:all",
            output_path,
        ]
        try:
            subprocess.run(
                exiftool_command,
                timeout=300,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Exiftool command failed for {input_path}: {e.stderr.strip()}")
            raise

        shutil.chown(output_path, original_stat.st_uid, original_stat.st_gid)
        os.chmod(output_path, original_stat.st_mode)
        os.utime(output_path, (original_stat.st_atime, original_stat.st_mtime))

        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            else:
                print(f"Original file not found for deletion: {input_path}")
        except PermissionError:
            print(f"Permission denied when trying to delete: {input_path}")
            raise
        except Exception as e:
            print(f"Error deleting original file {input_path}: {str(e)}")
            raise

        return True

    except subprocess.TimeoutExpired:
        print(f"Ghostscript command timed out after {timeout} seconds for {input_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error in Ghostscript command for {input_path}: {e.stderr}")
    except Exception as e:
        print(f"Unexpected error converting {input_path}: {str(e)}")
    return False
