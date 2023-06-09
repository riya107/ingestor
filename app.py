import os
import random
from flask import Flask, request
from dotenv import load_dotenv
from datetime import datetime
import logging
import config
from helpers import helpers
from config import logs
import codes
import pickle
from langchain.vectorstores import Chroma
from commonwords import common_words
from sentence_transformers import SentenceTransformer

load_dotenv()
app = Flask(__name__)
# Create directories if they don't exist
if not os.path.exists(config.DOCUMENTS_PATH):
    os.makedirs(config.DOCUMENTS_PATH)

if not os.path.exists(logs):
    os.makedirs(logs)

if not os.path.exists(config.CHROMADB_PATH):
    os.makedirs(config.CHROMADB_PATH)

if not os.path.exists(config.DOCSEARCH_PATH):
    os.makedirs(config.DOCSEARCH_PATH)

if not os.path.exists(config.EMBEDDINGS_STORE_PATH):
    os.makedirs(config.EMBEDDINGS_STORE_PATH)

# Generate a unique timestamp for the current run and configure logging
timestamp = datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
log_filename = f"processing_logs_{timestamp}.log"
log_filepath = os.path.join(logs, log_filename)

# Configure logging with the new log file
logging.basicConfig(filename=log_filepath, level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# Handle file uploads
@app.route('/upload', methods=['POST'])
def upload_documents():
    if 'documents' not in request.files:
        error_message = 'Missing required fields.'
        logging.error(error_message)
        return {'error': True, 'message': error_message}, 400

    documents = request.files.getlist('documents')
    random_number = random.randint(1000, 10000)
    directory_name = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')+'-'+str(random_number)
    logging.info(f'New upload request received at: {directory_name}')

    # Create a new directory for the uploaded documents using the current timestamp and random number
    os.makedirs(os.path.join(config.DOCUMENTS_PATH, directory_name))

    discarded_files = []
    total_files = len(documents)
    # Iterate over each uploaded file
    for file_data in documents:
        if file_data and helpers.allowed_file(file_data.filename):
            file_path = os.path.join(config.DOCUMENTS_PATH, directory_name, file_data.filename)
            file_data.save(file_path)
            logging.info(f'File {file_data.filename} has been uploaded.')
            logging.info(
                f'File {file_data.filename} is in {helpers.get_extension(file_data.filename)} format.')
        else:
            # Add discarded files to the list and log a warning message
            discarded_files.append(file_data.filename)
            logging.warning(
                f'File {file_data.filename} is discarded. Only txt, docx, and pdf files are allowed.')

    if len(discarded_files) == total_files:
        # If all files are discarded, delete the directory and return an error response
        os.rmdir(os.path.join(config.DOCUMENTS_PATH, directory_name))
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
        'document_path': directory_name, 'discarded_files': discarded_files}}
    logging.info(f'Response: {success_response}')
    return success_response, 200

# Store documents in the vector database
@app.route('/store_in_vectordb', methods=['POST'])
def store_in_vectordb():
    if 'document_path' not in request.get_json():
        error_message = 'Missing required fields.'
        logging.error(error_message)
        return {'error': True, 'message': error_message}, 400
    
    db_code = request.get_json().get('db_code')
    embedding_code = request.get_json().get('embedding_code')

    if db_code is not None and db_code not in codes.VECTOR_DATABASES:
        return {'error': True, 'message': 'Wrong db_code.'}, 400
    if embedding_code is not None and embedding_code not in codes.EMBEDDING_MODELS:
        return {'error': True, 'message': 'Wrong embedding_code.'}, 400
    
    document_path = request.get_json().get('document_path')
    if document_path not in os.listdir(config.DOCUMENTS_PATH):
        error_message = 'Invalid document_path.'
        logging.error(error_message)
        return {'error': True, 'message': error_message}, 400

    if not db_code:
        db_code = codes.DEFAULT_VD_MAP['default']


    if not embedding_code:
        embedding_code = codes.DEFAULT_EM_MAP['default']

    helpers.create_and_store_documents(document_path, db_code, embedding_code)
    logging.info('Embeddings are successfully stored in the vector database.')

    return {'error': False, 'message': 'Embeddings are successfully stored in vector database.'}, 200


@app.route('/search',methods=["POST"])
def answer_from_db():
    if 'query' not in request.get_json() or 'document_path' not in request.get_json():
        error_message = 'Missing required fields.'
        logging.error(error_message)
        return {'error': True, 'message': error_message}, 400

    document_path = request.get_json().get('document_path')
    query = request.get_json().get('query')

    if query.lower() in common_words:
        return {"error":"No results should be fetched based on attribute names"},200

    db_code = request.get_json().get('db_code')
    embedding_code = request.get_json().get('embedding_code')

    if db_code is not None and db_code not in codes.VECTOR_DATABASES:
        return {'error': True, 'message': 'Wrong db_code.'}, 400
    if embedding_code is not None and embedding_code not in codes.EMBEDDING_MODELS:
        return {'error': True, 'message': 'Wrong embedding_code.'}, 400
    
    document_path = request.get_json().get('document_path')
    if document_path not in os.listdir(config.DOCUMENTS_PATH):
        error_message = 'Invalid document_path.'
        logging.error(error_message)
        return {'error': True, 'message': error_message}, 400
    
    if not db_code:
        db_code = codes.DEFAULT_VD_MAP['default']

    if not embedding_code:
        embedding_code = codes.DEFAULT_EM_MAP['default']

    if embedding_code == '1':
        model = SentenceTransformer(codes.EMBEDDING_MODELS[embedding_code])
        embedding = helpers.create_sentence_transformers_embeddings(codes.EMBEDDING_MODELS[embedding_code])
    elif embedding_code == '2':
        model = SentenceTransformer(codes.EMBEDDING_MODELS[embedding_code])
        embedding = helpers.create_sentence_transformers_embeddings(codes.EMBEDDING_MODELS[embedding_code])

    collection_name = document_path+'-'+db_code+'-'+embedding_code

    if(db_code == '1'):
        docsearch = Chroma(persist_directory=config.CHROMADB_PATH, embedding_function=embedding, collection_name=collection_name)
    elif(db_code == '2'):
        file_name = document_path+'-'+db_code+'-'+embedding_code + '.pkl'
        with open(os.path.join(config.DOCSEARCH_PATH, file_name), 'rb') as file:
            docsearch = pickle.load(file)
 
    found_docs = docsearch.similarity_search_with_score(query, k=10)

    data=[]

    checksim=[]

    for text in found_docs:

        y=text[0].metadata['source']

        if y not in checksim:

         checksim.append(y)

         x=str(model.encode(text[0].page_content))

         data.append({"file_name":text[0].metadata['source'],"score":text[1],"content":text[0].page_content,"embeddings":x})

    return data,200

# Run the Flask application
if (__name__ == '__main__'):
    app.run(host=os.environ.get("HOSTIP"),
            port=os.environ.get("FLASK_RUN_PORT"), debug=True)
