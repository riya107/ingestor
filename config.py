import os
from langchain.text_splitter import TokenTextSplitter

DOCUMENTS_PATH = os.path.join(os.getcwd(), 'documents')

DOCSEARCH_PATH = os.path.join(os.getcwd(), 'docsearch')

CHROMADB_PATH = os.path.join(os.getcwd(), 'chromastore')

EMBEDDINGS_STORE_PATH = os.path.join(os.getcwd(), 'embeddings_store')

ALLOWED_EXTENSIONS = {'txt', 'docx', 'pdf'}

TEXT_SPLITTER = TokenTextSplitter(chunk_size=1500, chunk_overlap=50)

TYPESENSE_HOST = 'localhost'
TYPESENSE_PORT = '8108'
TYPESENSE_PROTOCOL = 'http'

logs = "logs"
