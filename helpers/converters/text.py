import os
import subprocess
import logging
import pymupdf 
from docx2pdf import convert as docx2pdf_convert

def convert_text(files, root):
    text_files = [f for f in files if f.lower().endswith(('.txt', '.pdf', '.docx'))]
    for text_file in text_files:
        input_path = os.path.join(root, text_file)
        output_path = os.path.splitext(input_path)[0] + '_PDFA.pdf'
        try:
            if text_file.lower().endswith('.txt'):
                # Convert TXT to PDF
                with open(input_path, 'r') as file:
                    text = file.read()
                doc = pymupdf.open() 
                page = doc.new_page()
                page.insert_text((72, 72), text)
                doc.save(output_path, garbage=4, deflate=True, clean=True)
                doc.close()
            elif text_file.lower().endswith('.pdf'):
                # Convert PDF to PDF/A-2b
                doc = pymupdf.open(input_path) 
                doc.save(output_path, garbage=4, deflate=True, clean=True, pdfa=2)
                doc.close()
            elif text_file.lower().endswith('.docx'):
                docx2pdf_convert(input_path, output_path)
                doc = pymupdf.open(output_path)  # Updated reference
                doc.save(output_path, garbage=4, deflate=True, clean=True, pdfa=2)
                doc.close()
            logging.info(f"Converted {text_file} to PDF/A-2b")
            os.remove(input_path)  # Remove the original text file
        except Exception as e:
            print(f"Error converting {text_file} to PDF/A-2b: {e}")
