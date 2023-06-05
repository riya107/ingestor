import os
from langchain.text_splitter import TokenTextSplitter

RESUMES_PATH = os.path.join(os.getcwd(), 'resumes')

VECTORDB_PATH = os.path.join(os.getcwd(), 'datastore')

ALLOWED_EXTENSIONS = {'txt', 'docx', 'pdf'}

TEXT_SPLITTER = TokenTextSplitter(chunk_size=200, chunk_overlap=10)

logs = "logs"
