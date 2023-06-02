import sqlite3
from chromadb import ChromaDB

# Specify the path and name of the database file
db_path = "resume.db"

# Create a connection to the database
conn = sqlite3.connect(db_path)

# Close the connection (
# optional, as it will be reopened when needed)
conn.close()
