import os
import config
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.vectorstores import Chroma

def allowed_file(filename):
    if '.' not in filename:
        return False
    if(filename.split('.')[1] in config.ALLOWED_EXTENSIONS):
        return True
    return False

def get_extension(filename):
    return filename.split('.')[1]

def create_and_store_documents(resume_path):
    resume_names = os.listdir(os.path.join(config.RESUMES_PATH, resume_path))
    documents = []
    for resume in resume_names:
        if resume.endswith('pdf'):
            loader = PyPDFLoader(os.path.join(config.RESUMES_PATH, resume_path, resume))
            documents.extend(config.TEXT_SPLITTER.split_documents(loader.load()))

        elif(resume.endswith('docx')):
            loader = Docx2txtLoader(os.path.join(config.RESUMES_PATH, resume_path, resume))
            documents.extend(config.TEXT_SPLITTER.split_documents(loader.load()))

        elif(resume.endswith('txt')):
            with open(os.path.join(config.RESUMES_PATH, resume_path, resume)) as f:
                text_file = f.read()
            documents.extend(config.TEXT_SPLITTER.create_documents([text_file], metadatas=[{'source': os.path.join(config.RESUMES_PATH, resume_path, resume)}]))
    
    vectordb = Chroma.from_documents(documents=documents, persist_directory=config.VECTORDB_PATH)
    vectordb.persist()