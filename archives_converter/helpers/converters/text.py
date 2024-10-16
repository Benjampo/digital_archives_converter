import os
import subprocess
import logging
import time
import shutil
from helpers.metadata import extract_metadata, append_metadata


def convert_pdfa(files, root):
    metadata_file = os.path.join(root, 'metadata.json')
    conversion_performed = False
    for file in files:
        if file.lower() in ['concat_list.txt', 'metadata.json', 'manifest-md5.txt', 'bagit.txt']:
            print(f"[bold yellow]Skipping:[/bold yellow] {file}")
            return conversion_performed
        
        input_path = os.path.join(root, file)
        output_path = os.path.splitext(input_path)[0] + '_pdfa.pdf'
        
        if file.lower().endswith('.pdf'):
            conversion_performed = convert_pdf_to_pdfa(input_path, output_path, metadata_file) or conversion_performed
        elif file.lower().endswith(('.txt', '.doc', '.docx', '.rtf', '.odt')):
            conversion_performed = convert_to_pdf(input_path, output_path, metadata_file) or conversion_performed
        
        original_file = output_path.replace('.pdf', '.pdf_original')
        if os.path.exists(original_file):
            os.remove(original_file)
    
    return conversion_performed

def convert_to_pdf(input_path, output_path, metadata_file):
    try:
        original_stat = os.stat(input_path)
        
        # Extract metadata before conversion
        metadata = extract_metadata(input_path)
        
        unoconv_command = [
            'unoconv',
            '-f', 'pdf',
            '-eSelectPdfVersion=2',
            '-ePDFACompliance=2',
            '-o', output_path,
            input_path
        ]
        subprocess.run(unoconv_command, timeout=60, check=True, capture_output=True, text=True)
        
        exiftool_command = [
            'exiftool',
            '-tagsFromFile', input_path,
            '-all:all',
            output_path
        ]
        subprocess.run(exiftool_command, timeout=60, check=True, capture_output=True, text=True)
        

        shutil.chown(output_path, original_stat.st_uid, original_stat.st_gid)
        os.chmod(output_path, original_stat.st_mode)
        
        # Set original file's timestamps on the new file
        os.utime(output_path, (original_stat.st_atime, original_stat.st_mtime))
        
     
        append_metadata(metadata, metadata_file, input_path)
        
        os.remove(input_path)  # Remove the original text file
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error converting {input_path} to PDF/A-2b: {e.stderr}")
    except Exception as e:
        logging.error(f"Unexpected error converting {input_path}: {str(e)}")
    return False

def convert_pdf_to_pdfa(input_path, output_path, metadata_file):
    try:
        original_stat = os.stat(input_path)
        
        # Extract metadata before conversion
        metadata = extract_metadata(input_path)
        
        gs_command = [
            'gs', '-dPDFA=2', '-dBATCH', '-dNOPAUSE',
            '-sColorConversionStrategy=UseDeviceIndependentColor',
            '-sProcessColorModel=DeviceCMYK', '-sDEVICE=pdfwrite',
            '-dPDFACompatibilityPolicy=1',
            '-dOverwritePDFMark=true',
            f'-sOutputFile={output_path}',
            input_path
        ]
        
        start_time = time.time()
        process = subprocess.Popen(gs_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
      
        timeout = 300
        while process.poll() is None:
            if time.time() - start_time > timeout:
                process.kill()
                raise subprocess.TimeoutExpired(gs_command, timeout)
            time.sleep(1)
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, gs_command, stdout, stderr)


        exiftool_command = [
            'exiftool',
            '-tagsFromFile', input_path,
            '-all:all',
            output_path
        ]
        subprocess.run(exiftool_command, timeout=300, check=True, capture_output=True, text=True)
        

        shutil.chown(output_path, original_stat.st_uid, original_stat.st_gid)
        os.chmod(output_path, original_stat.st_mode)
        
        # Set original file's timestamps on the new file
        os.utime(output_path, (original_stat.st_atime, original_stat.st_mtime))
        
 
        append_metadata(metadata, metadata_file, output_path)        
        # Also check for the input file itself
        if os.path.exists(input_path):
            os.remove(input_path)
        return True

    except subprocess.TimeoutExpired:
        logging.error(f"Ghostscript command timed out after {timeout} seconds for {input_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error in Ghostscript command for {input_path}: {e.stderr}")
    except Exception as e:
        logging.error(f"Unexpected error converting {input_path}: {str(e)}")
    return False


