import os
from langchain.vectorstores import Chroma
from langchain.vectorstores import Typesense

VECTOR_DATABASES = {
    '1' : 'chromadb',
    '2' : 'typesense',
    'default' : 'chromadb'
}

EMBEDDING_MODELS = {
    '1' : 'multi-qa-mpnet-base-dot-v1',
    '2' : 'all-mpnet-base-v2',
    'default' : 'multi-qa-mpnet-base-dot-v1'
}

DEFAULT_VD_MAP = {
    'default' : '1'
}

DEFAULT_EM_MAP = {
    'default' : '1'
}