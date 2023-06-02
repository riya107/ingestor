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

# Configure logging
logs_folder = "logs"
if not os.path.exists(logs_folder):
    os.makedirs(logs_folder)

# Generate a unique timestamp for the current run
timestamp = datetime.datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
log_filename = f"processing_logs_{timestamp}.log"
log_filepath = os.path.join(logs_folder, log_filename)

# Configure logging with the new log file
logging.basicConfig(filename=log_filepath, level=logging.INFO, format='%(asctime)s - %(message)s')

# Load pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

max_sequence_length = 512  # Maximum sequence length supported by the model

# Function to generate embeddings for a given resume

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

class ResumeProcessorWithEmbedding(ResumeProcessor):
    def __init__(self, processed_folder, embedding_folder):
        super().__init__(processed_folder, processed_folder)
        self.embedding_folder = embedding_folder
        self.client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./store/" # Optional, defaults to .chromadb/ in the current directory
))
        self.collection = self.client.create_collection(name="resume_embeddings", embedding_function=custom_emb_func)

    def preprocess_resumes(self):
        print("**********",self.folder)
        # Process each resume in the processed folder
        for filename in os.listdir(self.folder):
            print(filename,">>>>>>>>>>>")
            if filename.endswith('.txt'):
                preprocessed_resume = self._preprocess_resume(filename)
                # Generate the embedding vector
                logging.info(f"Calculating embedding vector for {filename}...")
                # embedding_vector = generate_resume_embedding(preprocessed_resume)
                # embedding_vector = embedding_vector.tolist()
                # Store the embedding vector in ChromaDB
                self.collection.add(documents=[preprocessed_resume], ids=[filename])
                logging.info(f"Embedding vector for {filename} is stored in ChromaDB\n\n")
                logging.info(f"Embedding vector for {filename} is stored in ChromaDB\n\n")

    def _preprocess_resume(self, filename):
        # Load the resume text from the file
        with open(os.path.join(self.folder, filename), 'r') as f:
            resume = f.read()

        # Log that the file is under preprocessing
        logging.info(f"{filename} is under preprocessing at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Preprocess the resume
        preprocessed_resume = self._preprocess_text(resume)

        logging.info(f"Preprocessed text of {filename}:\n{preprocessed_resume}")
        # Log that the file has been moved to the processed folder
        logging.info(f"{filename} is moved to processed folder as {filename}")

        # Return the processed resume
        return preprocessed_resume


# Specify the path to the processed folder
processed_folder = "processed"

# Specify the path to the embedding folder
embedding_folder = "ENGINEERING"

# Create an instance of the ResumeProcessorWithEmbedding
resume_processor = ResumeProcessorWithEmbedding(processed_folder, embedding_folder)

# Preprocess the resumes and generate embeddings
# resume_processor.preprocess_resumes()

# l=resume_processor.collection.get(
#     include=["documents"],

# )


