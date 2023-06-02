
import os
import logging
import time
from func import ResumeProcessor
import datetime
from transformers import BertTokenizer, BertModel
import torch
import numpy as np
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from chromadb.config import Settings

class MyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, texts: Documents) -> Embeddings:
        # embed the documents somehow
        embeddings = []
        for text in texts:
            embeddings.append(generate_resume_embedding(text))
        return embeddings
    
custom_emb_func = MyEmbeddingFunction()
    

def generate_resume_embedding(resume):
    # Tokenize the resume text and truncate if necessary
    tokens = tokenizer.encode(resume, add_special_tokens=True, max_length=max_sequence_length, truncation=True)
    input_ids = torch.tensor([tokens])

    # Obtain the BERT embeddings
    with torch.no_grad():
        outputs = model(input_ids)
        embeddings = outputs.last_hidden_state.squeeze(0)  # Remove batch dimension

    # Perform any necessary pooling or aggregation over the token embeddings
    aggregated_embedding = embeddings.mean(dim=0)  # Example: Average pooling

    # Convert the tensor to a numpy array or any other suitable format
    resume_embedding = aggregated_embedding.numpy()

    return resume_embedding.tolist()


client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./store/" # Optional, defaults to .chromadb/ in the current directory
))

collection = client.get_collection(name="resume_embeddings", embedding_function=custom_emb_func)

print(collection.get(include=["embeddings"]))