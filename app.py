import os
from flask import Flask, request
from dotenv import load_dotenv
from datetime import datetime
import logging
import config
from helpers import helpers
from config import logs


load_dotenv()
app = Flask(__name__)
# Create directories if they don't exist
if not os.path.exists(config.RESUMES_PATH):
    os.makedirs(config.RESUMES_PATH)

if not os.path.exists(config.VECTORDB_PATH):
    os.makedirs(config.VECTORDB_PATH)


if not os.path.exists(logs):
    os.makedirs(logs)

# Generate a unique timestamp for the current run and configure logging
timestamp = datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
log_filename = f"processing_logs_{timestamp}.log"
log_filepath = os.path.join(logs, log_filename)

# Configure logging with the new log file
logging.basicConfig(filename=log_filepath, level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# Handle file uploads


@app.route('/upload', methods=['POST'])
def upload_resumes():
    if 'resumes' not in request.files:
        error_message = 'Missing required fields.'
        logging.error(error_message)
        return {'error': True, 'message': error_message}, 400

    resumes = request.files.getlist('resumes')
    timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
    logging.info(f'New upload request received at: {timestamp}')

    # Create a new directory for the uploaded resumes using the current timestamp
    os.makedirs(os.path.join(config.RESUMES_PATH, timestamp))

    discarded_files = []
    total_files = len(resumes)
    # Iterate over each uploaded file
    for idx, file_data in enumerate(resumes):
        if file_data and helpers.allowed_file(file_data.filename):
            # Generate a unique filename and save the file to the appropriate path
            filename = f'resume_{idx+1}.{helpers.get_extension(file_data.filename)}'
            file_path = os.path.join(config.RESUMES_PATH, timestamp, filename)
            file_data.save(file_path)
            logging.info(f'File {filename} has been uploaded.')
            logging.info(
                f'File {filename} is in {helpers.get_extension(file_data.filename)} format.')
        else:
            # Add discarded files to the list and log a warning message
            discarded_files.append(file_data.filename)
            logging.warning(
                f'File {file_data.filename} is discarded. Only txt, docx, and pdf files are allowed.')

    if len(discarded_files) == total_files:
        # If all files are discarded, delete the directory and return an error response
        os.rmdir(os.path.join(config.RESUMES_PATH, timestamp))
        error_message = 'Only txt, docx, and pdf files are allowed.'
        logging.error(error_message)
        return {'error': True, 'message': error_message}, 400

    uploaded_files = total_files - len(discarded_files)

    if len(discarded_files) == 0:
        message = 'Files uploaded successfully.'
    else:
        message = f'Uploaded files: {uploaded_files}, Discarded Files {len(discarded_files)}.'
    # Prepare and return the success response
    success_response = {'error': False, 'message': message, 'response': {
        'resume_path': timestamp, 'discarded_files': discarded_files}}
    logging.info(f'Response: {success_response}')
    return success_response, 200

# Store resumes in the vector database


@app.route('/store_in_vectordb', methods=['POST'])
def store_in_vectordb():
    if 'resume_path' not in request.get_json():
        error_message = 'Missing required fields.'
        logging.error(error_message)
        return {'error': True, 'message': error_message}, 400

    resume_path = request.get_json().get('resume_path')

    if resume_path not in os.listdir(config.RESUMES_PATH):
        error_message = 'Invalid resume_path.'
        logging.error(error_message)
        return {'error': True, 'message': error_message}, 400

    helpers.create_and_store_documents(resume_path)
    logging.info('Embeddings are successfully stored in the vector database.')

    return {'error': False, 'message': 'Embeddings are successfully stored in vector database.'}, 200


# Run the Flask application
if (__name__ == '__main__'):
    app.run(host=os.environ.get("HOSTIP"),
            port=os.environ.get("FLASK_RUN_PORT"), debug=True)
