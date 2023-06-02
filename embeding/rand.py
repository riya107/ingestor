import os
import logging
import sqlite3
import datetime
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
# Configure logging
import string
logs_folder = "randlogs"
if not os.path.exists(logs_folder):
    os.makedirs(logs_folder)

# Generate a unique timestamp for the current run
timestamp = datetime.datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
log_filename = f"processing_logs_{timestamp}.log"
log_filepath = os.path.join(logs_folder, log_filename)

# Configure logging with the new log file
logging.basicConfig(filename=log_filepath, level=logging.INFO, format='%(asctime)s - %(message)s')

# # Connect to the SQLite database
conn = sqlite3.connect('resumes.db')
# cur=conn.cursor()
# # Create the resumes table if it doesn't exist
# cu=cur.execute('''CREATE TABLE IF NOT EXISTS resumes (
#                     name TEXT PRIMARY KEY,
#                     resume_text TEXT NOT NULL
#                 );''')

# print(cu.fetchone())


# class ResumeProcessor:
#     def __init__(self, db_connection, processed_folder):
#         self.db_connection = db_connection
#         self.processed_folder = processed_folder

#     def _is_resume_processed(self, name):
#         cursor = self.db_connection.cursor()
#         cursor.execute("SELECT * FROM resumes WHERE name = ?", (name,))
#         return cursor.fetchone() is not None

#     def process_resumes(self):
#         # Process each resume in the unprocessed folder
#         for filename in os.listdir(self.processed_folder):
#             if filename.endswith('.txt'):
#                 name, phone_number, resume_text = self._extract_resume_info(filename)

#                 if self._is_resume_processed(name):
#                     logging.info(f"Resume for {name} is already processed. Skipping...")
#                     continue

#                 # Preprocess the resume
#                 preprocessed_resume = self._preprocess_text(resume_text)

#                 # Save the processed resume to the database
#                 self.db_connection.execute("INSERT INTO resumes (name, phone_number, resume_text) VALUES (?, ?, ?)",
#                                            (name, phone_number, preprocessed_resume))
#                 self.db_connection.commit()

#                 logging.info(f"Resume for {name} processed and saved to the database.")

#     def _extract_resume_info(self, filename):
#         # Extract name and phone number from the file
#         with open(os.path.join(self.processed_folder, filename), 'r') as f:
#             resume_lines = f.readlines()
#             name = resume_lines[0].strip().split()[0]
#             phone_number = resume_lines[0].strip().split()[1]
#             resume_text = ''.join(resume_lines[1:])  # Exclude the first line (name and phone number)

#         logging.info(f"Processing resume: {filename}")
#         logging.info(f"Name: {name}")
#         logging.info(f"Phone number: {phone_number}")

#         return name, phone_number, resume_text

#     def _preprocess_text(self, text):
#         # Convert text to lowercase
#         text = text.lower()

#         # Remove punctuation
#         text = text.translate(str.maketrans('', '', string.punctuation))

#         # Remove special characters
#         text = re.sub(r"[^a-zA-Z0-9]", " ", text)

#         # Tokenize the text into individual words
#         tokens = nltk.word_tokenize(text)

#         # Remove stopwords
#         stop_words = set(stopwords.words('english'))
#         tokens = [word for word in tokens if word not in stop_words]

#         # Lemmatize words
#         lemmatizer = WordNetLemmatizer()
#         tokens = [lemmatizer.lemmatize(word) for word in tokens]

#         # Join the tokens back into a single string
#         preprocessed_text = ' '.join(tokens)

#         return preprocessed_text

# # Specify the path to the processed folder
# processed_folder = "processed"

# # Create an instance of the ResumeProcessor with the database connection and processed folder
# resume_processor = ResumeProcessor(conn, processed_folder)

# # Process resumes
# resume_processor.process_resumes()

# Close the database connection


# Fetch all rows from the resumes table
cursor = conn.execute("SELECT * FROM resumes")
rows = cursor.fetchall()

# Print the fetched content
for row in rows:
    logging.info(f"Name: {row[0]}")
    logging.info(f"Phone number: {row[1]}")
    logging.info(f"Resume text: {row[2]}")
    logging.info("-------------------")

conn.close()