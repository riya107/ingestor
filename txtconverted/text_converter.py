import os
import datetime
import logging
from PyPDF2 import PdfReader
from PyPDF2 import PdfFileReader
from docx import Document
from config import *

class ResumeProcessor:
    def __init__(self, resumes_folder, output_folder):
        self.resumes_folder = resumes_folder
        self.output_folder = output_folder

    def process_resumes(self):
        # Configure logging
        logs = logs_folder
        if not os.path.exists(logs):
            os.makedirs(logs)

        # Generate a unique timestamp for the current run
        timestamp = datetime.datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
        log_filename = f"processing_logs_{timestamp}.log"
        log_filepath = os.path.join(logs, log_filename)

        # Configure logging with the new log file
        logging.basicConfig(filename=log_filepath, level=logging.INFO, format='%(asctime)s - %(message)s')

        # Iterate over the files in the resumes folder
        for filename in os.listdir(self.resumes_folder):
            filepath = os.path.join(self.resumes_folder, filename)
            if os.path.isfile(filepath):
                file_format = self.get_file_format(filename)
                if file_format == 'pdf':
                    converted_filepath = self.convert_pdf_to_txt(filepath)
                elif file_format == 'docx':
                    converted_filepath = self.convert_docx_to_txt(filepath)
                elif file_format == 'txt':
                    converted_filepath = filepath
                else:
                    logging.error(f"Unsupported file format: {file_format} - File: {filename}")
                    continue

                # Move the converted file to the output folder
                self.move_file(converted_filepath, self.output_folder)

                logging.info(f"File {filename} is in {file_format} format, converted to TXT, and moved to {self.output_folder}")

    @staticmethod
    def get_file_format(filename):
        _, extension = os.path.splitext(filename)
        return extension[1:].lower()

    @staticmethod
    def convert_pdf_to_txt(filepath):
        try:
            pdf = PdfReader(filepath)
            text = ''
            for page in pdf.pages:
                text += page.extract_text()
            converted_filepath = os.path.splitext(filepath)[0] + ".txt"
            with open(converted_filepath, 'w', encoding='utf-8') as file:
                file.write(text)
            return converted_filepath
        except Exception as e:
            logging.error(f"Error converting PDF to TXT - File: {filepath} - Error: {str(e)}")
            return None

    @staticmethod
    def convert_docx_to_txt(filepath):
        try:
            doc = Document(filepath)
            text = ' '.join([paragraph.text for paragraph in doc.paragraphs])
            converted_filepath = os.path.splitext(filepath)[0] + ".txt"
            with open(converted_filepath, 'w', encoding='utf-8') as file:
                file.write(text)
            return converted_filepath
        except Exception as e:
            logging.error(f"Error converting DOCX to TXT - File: {filepath} - Error: {str(e)}")
            return None

    @staticmethod
    def move_file(filepath, destination_folder):
        try:
            if filepath is not None:
                os.makedirs(destination_folder, exist_ok=True)
                destination = os.path.join(destination_folder, os.path.basename(filepath))
                os.replace(filepath, destination)
            else:
                logging.error(f"Error moving file - File: {filepath} - Destination: {destination_folder} - File conversion failed.")
        except Exception as e:
            logging.error(f"Error moving file - File: {filepath} - Destination: {destination_folder} - Error: {str(e)}")

# Example usage 
resumes_folder = input_resume
output_folder = output_resume
if not os.path.exists(resumes_folder):
            os.makedirs(resumes_folder)
if not os.path.exists(output_folder):
            os.makedirs(output_folder)

processor = ResumeProcessor(resumes_folder, output_folder)
processor.process_resumes()

