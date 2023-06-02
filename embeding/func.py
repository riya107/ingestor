import os
import shutil
import logging
import time
import string
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


class ResumeProcessor:
    def __init__(self, folder, processed_folder):
        self.folder = folder
        self.processed_folder = processed_folder

    def _preprocess_text(self, text):
        # Convert text to lowercase
        text = text.lower()

        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))

        # Remove special characters
        text = re.sub(r"[^a-zA-Z0-9]", " ", text)

        # Tokenize the text into individual words
        tokens = nltk.word_tokenize(text)

        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]

        # Lemmatize words
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(word) for word in tokens]

        # Join the tokens back into a single string
        preprocessed_text = ' '.join(tokens)

        return preprocessed_text

    def _preprocess_resume(self, filename):
        # Load the resume text from the file
        with open(os.path.join(self.folder, filename), 'r') as f:
            resume = f.read()

        # Log that the file is under preprocessing
        logging.info(f"{filename} is under preprocessing at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Preprocess the resume
        preprocessed_resume = self._preprocess_text(resume)

        with open(os.path.join(self.processed_folder, filename), 'w') as f:
            f.write(preprocessed_resume)
        # # Dump the preprocessed text with the respective file name
        # with open(os.path.join(self.processed_folder, f"{filename}.txt"), 'w') as f:
        #     f.write(f"{preprocessed_resume}")

        logging.info(f"Preprocessed text of {filename} is:\n{preprocessed_resume}")
        # Log that the file has been moved to the processed folder
        logging.info("\n")
        
        logging.info(f"{filename} is moved to processed folder as {filename}")

        # Move the file from the unprocessed folder to the processed folder
        os.remove(os.path.join(self.folder, filename))

        # Return the processed resume
        return preprocessed_resume

    def preprocess_resumes(self):
        # Create the processed folder if it doesn't exist
        if not os.path.exists(self.processed_folder):
            os.makedirs(self.processed_folder)

        # Process each resume in the unprocessed folder
        for filename in os.listdir(self.folder):
            if filename.endswith('.txt'):
                self._preprocess_resume(filename)


# Configure logging
# logging.basicConfig(filename='processing_logs.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Specify the path to the unprocessed folder
unprocessed_folder = "unprocessed"

# Specify the path to the processed folder
processed_folder = "processed"

# Create an instance of the ResumeProcessor
resume_processor = ResumeProcessor(unprocessed_folder, processed_folder)

# Preprocess the resumes and move them to the processed folder
resume_processor.preprocess_resumes()
