import os
import subprocess
import logging


def convert_text(files, root):
    text_files = [f for f in files if f.lower().endswith(('.txt', '.doc','.pdf', '.docx', '.rtf', '.odt'))]
    for text_file in text_files:

        input_path = os.path.join(root, text_file)
        output_path = os.path.splitext(input_path)[0] + '.pdf'
        try:
            unoconv_command = [
                'unoconv',
                '-f', 'pdf',
                '-eSelectPdfVersion=2',
                '-ePDFACompliance=2',
                '-o', output_path,
                input_path
            ]
            result = subprocess.run(unoconv_command, timeout=600, check=True, capture_output=True, text=True)
            os.remove(input_path)  # Remove the original text file
        except subprocess.CalledProcessError as e:
            logging.error(f"Error converting {text_file} to PDF/A-2b: {e.stderr}")
        except Exception as e:
            logging.error(f"Unexpected error converting {text_file}: {str(e)}")
