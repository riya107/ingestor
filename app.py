import os
from flask import Flask, request
from dotenv import load_dotenv
from datetime import datetime
import config
from helpers import helpers

load_dotenv()

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_resumes():
    if 'resumes' not in request.files:
        return {'error': True, 'message': 'Missing required fields.'}, 400

    resumes = request.files.getlist('resumes')
    timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')

    os.makedirs(os.path.join(config.RESUMES_PATH, timestamp))

    discarded_files = []
    total_flies = len(resumes)

    for idx, file_data in enumerate(resumes):
        if file_data and helpers.allowed_file(file_data.filename):
            filename = f'resume_{idx+1}.{helpers.get_extension(file_data.filename)}'
            file_path = os.path.join(config.RESUMES_PATH, timestamp, filename)
            file_data.save(file_path)
        else:
            discarded_files.append(file_data.filename)

    if len(discarded_files) == total_flies:
        return {'error': True, 'message': 'Only txt, docx, and pdf files are allowed.'}, 400

    uploaded_files = total_flies - len(discarded_files)

    if len(discarded_files) == 0:
        message = 'Files uploaded successfully.'
    else:
        message = f'{uploaded_files} are uploaded successfully. {len(discarded_files)} are discarded.'

    return {'error': False, 'message': message, 'response': {'resume_path': timestamp, 'discared_files': discarded_files}}, 200


@app.route('/store_in_vectordb', methods=['POST'])
def store_in_vectordb():
    if 'resume_path' not in request.get_json():
        return {'error': True, 'message': 'Missing required fields.'}, 400   

    resume_path = request.get_json().get('resume_path')

    if resume_path not in os.listdir(config.RESUMES_PATH):
        return {'error': True, 'message': 'Invalid resume_path.'}, 400
    
    helpers.create_and_store_documents(resume_path)

    return {'error': False, 'message': 'Embeddings are successfully stored in vector database.'}, 200

if (__name__ == '__main__'):
    app.run(host=os.environ.get("HOSTIP"),
            port=os.environ.get("FLASK_RUN_PORT"), debug=True)
