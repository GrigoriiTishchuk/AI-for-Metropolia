import requests
from readability import Document
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

''' Example output chunk:
{
  "url": "https://example.com",
  "chunk_index": 0,
  "text": "Helsinki Cathedral is a major tourist attraction ...",
  "embedding": [0.12, -0.55, ... 384 floats ...]
}
'''

def fetch_text_from_url(url: str) -> str:
    response = requests.get(url)
    html = response.text

    # Use Readability to extract main content
    doc = Document(html)
    readable_html = doc.summary()

    # Parse readable HTML
    soup = BeautifulSoup(readable_html, "html.parser")

    # Extract text only
    text = soup.get_text(separator="\n")

    # Clean up whitespace
    clean_text = "\n".join([line.strip() for line in text.split("\n") if line.strip() != ""])
    return clean_text


def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,     # 800–1500 is ideal for RAG
        chunk_overlap=200,   # maintain context
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""]
    )
    return splitter.split_text(text)

embedder = SentenceTransformer("all-MiniLM-L6-v2")  # Lightweight, free, fast

def embed_chunks(chunks):
    embeddings = embedder.encode(chunks, convert_to_numpy=True)
    return embeddings


def process_url(url: str):
    text = fetch_text_from_url(url)
    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks)

    processed = []
    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        processed.append({
            "url": url,
            "chunk_index": idx,
            "text": chunk,
            "embedding": emb.tolist()
        })
    return processed