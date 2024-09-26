import os
import subprocess
import logging


def convert_text(files, root):
    for file in files:
        if file.lower() == 'concat_list.txt':
            print(f"Skipping concat_list.txt: {file}")
            continue
        
        input_path = os.path.join(root, file)
        output_path = os.path.splitext(input_path)[0] + '_pdfa.pdf'
        
        if file.lower().endswith('.pdf'):
            convert_pdf_to_pdfa(input_path, output_path)
        elif file.lower().endswith(('.txt', '.doc', '.docx', '.rtf', '.odt')):
            convert_to_pdf(input_path, output_path)
        else:
            print(f"Skipping unsupported file: {file}")


def convert_to_pdf(input_path, output_path):
    try:
        unoconv_command = [
            'unoconv',
            '-f', 'pdf',
            '-eSelectPdfVersion=2',
            '-ePDFACompliance=2',
            '-o', output_path,
            input_path
        ]
        subprocess.run(unoconv_command, timeout=600, check=True, capture_output=True, text=True)
        os.remove(input_path)  # Remove the original text file
    except subprocess.CalledProcessError as e:
        logging.error(f"Error converting {input_path} to PDF/A-2b: {e.stderr}")
    except Exception as e:
        logging.error(f"Unexpected error converting {input_path}: {str(e)}")


def convert_pdf_to_pdfa(input_path, output_path):
    try:
        gs_command = [
            'gs', '-dPDFA=2', '-dBATCH', '-dNOPAUSE',
            '-sColorConversionStrategy=UseDeviceIndependentColor',
            '-sProcessColorModel=DeviceCMYK', '-sDEVICE=pdfwrite',
            '-dPDFACompatibilityPolicy=1',
            f'-sOutputFile={output_path}',
            input_path
        ]
        subprocess.run(gs_command, timeout=600, check=True, capture_output=True, text=True)
        os.remove(input_path)  # Remove the original PDF file
    except subprocess.CalledProcessError as e:
        logging.error(f"Error converting {input_path} to PDF/A-2b: {e.stderr}")
    except Exception as e:
        logging.error(f"Unexpected error converting {input_path}: {str(e)}")
