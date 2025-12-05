# db_store.py
import psycopg2
from extraction_to_chunks import process_url
from dotenv import load_dotenv
import os

load_dotenv()

# PostgreSQL connection
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)
cur = conn.cursor()

# Create tables (if not exists)
cur.execute("""
CREATE EXTENSION IF NOT EXISTS vector;
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS messages (
    message_id UUID PRIMARY KEY,
    chat_id UUID REFERENCES chats(chat_id),
    sender TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS chats (
    chat_id UUID PRIMARY KEY,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    chunk_index INT NOT NULL,
    text TEXT NOT NULL,
    embedding VECTOR(384) NOT NULL  -- match your embedding size
);
""")
conn.commit()


# Function to store chunks
def store_chunks(url: str):
    # 1. Generate chunks with embeddings
    processed_chunks = process_url(url)
    # 2. Insert into PostgreSQL
    for chunk in processed_chunks:
        cur.execute("""
            INSERT INTO chunks (url, chunk_index, text, embedding)
            VALUES (%s, %s, %s, %s)
        """, (chunk["url"], chunk["chunk_index"], chunk["text"], chunk["embedding"]))
    conn.commit()
    print(f"Stored {len(processed_chunks)} chunks for URL: {url}")


# Example usage
if __name__ == "__main__":
    urls = [
        "https://www.metropolia.fi/fi",
        "https://www.metropolia.fi/en", 
        "https://opinto-opas.metropolia.fi",
        "https://opinto-opas.metropolia.fi/88094/fi/67/70361/3635/2643", 
        "https://opinto-opas.metropolia.fi/88094/fi/67/70361",
        "https://opinto-opas.metropolia.fi?lang=en",
        "https://opinto-opas.metropolia.fi/88094/fi/67/70361/3635/2643?lang=en", 
        "https://opinto-opas.metropolia.fi/88094/fi/67/70361?lang=en"
    ]
    for url in urls:
        store_chunks(url)
    cur.close()
    conn.close()
    print("All done!")
