import os
import config
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.vectorstores import Chroma
from langchain.vectorstores import Typesense
from langchain.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
import codes
import pickle

# Check if the file extension is allowed
def allowed_file(filename):
    if '.' not in filename:
        return False
    if (filename.split('.')[1] in config.ALLOWED_EXTENSIONS):
        return True
    return False

# Get the file extension from the filename
def get_extension(filename):
    return filename.split('.')[1]

# Create pickle file
def create_pickle_file(obj, file_name):
    with open(os.path.join(config.DOCSEARCH_PATH,file_name), 'wb') as file:
        pickle.dump(obj, file)


# Create sentence transformers embeddings
def create_sentence_transformers_embeddings(embedding_model):
    model_name = f'sentence-transformers/{embedding_model}'
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}

    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    return hf

def embed_documents_with_hugging_face(document_path, db_code, embedding_code, documents):
    model = SentenceTransformer(codes.EMBEDDING_MODELS[embedding_code])
    file_name = document_path + '-' + db_code + '-' + embedding_code + '.txt'
    with open(os.path.join(config.EMBEDDINGS_STORE_PATH, file_name), "w",encoding="utf-8") as file:
        for texts in documents:
            file.write(f'\nFile_name: {texts.metadata["source"]}\n\n')
            file.write(str(model.encode(texts.page_content))+'\n')
    
    
# Store embeddings in typesense vector database
def store_in_typesense(document_path, db_code, embedding_code, documents, embedding):
    collection_name = document_path + '-' + db_code + '-' + embedding_code
    return Typesense.from_documents(documents,
                                     embedding,
                                     typesense_client_params={
                                         'host': config.TYPESENSE_HOST,
                                         'port': config.TYPESENSE_PORT,
                                         'protocol': config.TYPESENSE_PROTOCOL,
                                         'typesense_api_key': os.environ.get('TYPESENSE_API_KEY'),
                                         'typesense_collection_name': collection_name
                                     })

# Create and store documents in the vector database
def create_and_store_documents(document_path, db_code, embedding_code):
    document_names = os.listdir(os.path.join(config.DOCUMENTS_PATH, document_path))
    documents = []
    for document in document_names:
        # Load and split PDF documents
        if document.endswith('pdf'):
            loader = PyPDFLoader(os.path.join(
                config.DOCUMENTS_PATH, document_path, document))
            documents.extend(
                config.TEXT_SPLITTER.split_documents(loader.load()))
        # Load and split DOCX documents
        elif (document.endswith('docx')):
            loader = Docx2txtLoader(os.path.join(
                config.DOCUMENTS_PATH, document_path, document))
            documents.extend(
                config.TEXT_SPLITTER.split_documents(loader.load()))
        # Load and split TXT documents
        elif (document.endswith('txt')):
            with open(os.path.join(config.DOCUMENTS_PATH, document_path, document), encoding='utf-8') as f:
                text_file = f.read()
            documents.extend(config.TEXT_SPLITTER.create_documents([text_file], metadatas=[
                             {'source': os.path.join(config.DOCUMENTS_PATH, document_path, document)}]))
    
    if embedding_code == 'default':
        embedding = create_sentence_transformers_embeddings(codes.EMBEDDING_MODELS[embedding_code])
        embed_documents_with_hugging_face(document_path, db_code, embedding_code, documents)
    elif embedding_code in ['1', '2']:
        embedding = create_sentence_transformers_embeddings(codes.EMBEDDING_MODELS[embedding_code])
        embed_documents_with_hugging_face(document_path, db_code, embedding_code, documents)
    
    if db_code == 'default':
        collection_name = document_path + '-' + db_code + '-' + embedding_code
        db = Chroma.from_documents(documents, embedding, persist_directory=config.CHROMADB_PATH, collection_name=collection_name)
        db.persist()

    elif db_code == '1':
        collection_name = document_path + '-' + db_code + '-' + embedding_code
        db = Chroma.from_documents(documents, embedding, persist_directory=config.CHROMADB_PATH, collection_name=collection_name)
        db.persist()
        
    elif db_code == '2':
        db = store_in_typesense(document_path, db_code, embedding_code, documents, embedding)
        create_pickle_file(db, f'{document_path}-{db_code}-{embedding_code}.pkl')
