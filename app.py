from flask import Flask, request, jsonify
import json
from uuid import uuid4
import psycopg2
import requests
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv
import os
from flask_cors import CORS

# Setup section
app = Flask(__name__)
CORS(app)
load_dotenv()

# PostgreSQL connection
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

embedder = SentenceTransformer("all-MiniLM-L6-v2")
# Helper: Chat management
def get_or_create_chat(chat_id=None):
    cur = conn.cursor()
    if chat_id:
        cur.execute("SELECT chat_id FROM chats WHERE chat_id=%s;", (chat_id,))
        if cur.fetchone():
            return chat_id
    # Create a new chat with random UUID
    new_chat = str(uuid4())
    cur.execute("INSERT INTO chats (chat_id) VALUES (%s);", (new_chat,))
    conn.commit()
    return new_chat


def save_message(chat_id, sender, content):
    cur = conn.cursor()
    message_id = str(uuid4())
    cur.execute("""
        INSERT INTO messages (message_id, chat_id, sender, content)
        VALUES (%s, %s, %s, %s);
    """, (message_id, chat_id, sender, content))
    conn.commit()


def load_history(chat_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT sender, content FROM messages
        WHERE chat_id=%s ORDER BY timestamp ASC;
    """, (chat_id,))
    rows = cur.fetchall()

    messages = []
    for sender, content in rows:
        role = "user" if sender == "user" else "assistant"
        messages.append({"role": role, "content": content})
    return messages


# Retriever with pgvector
def retrieve_top_k(query_embedding, k=3):
    # Ensure Python floats
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    cur = conn.cursor()
    # Use the vector literal syntax for pgvector
    # e.g., '[0.1, 0.2, 0.3]'::vector
    vector_literal = '[' + ','.join(map(str, query_embedding)) + ']'
    cur.execute(f"""
        SELECT text
        FROM chunks
        ORDER BY embedding <-> '{vector_literal}'::vector
        LIMIT %s;
    """, (k,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [r[0] for r in rows]

#Ask LLM with RAG
def ask_llm(history, retrieved_chunks):
    system_prompt = (
        "You are a helpful assistant. "
        "Use the following retrieved context to answer the user's question. "
        "If the context does not contain the information, say so.\n\n"
        "### Retrieved context ###\n"
        + "\n\n".join(retrieved_chunks)
        + "\n### End of context ###\n"
    )

    full_messages = [{"role": "system", "content": system_prompt}] + history
    res = requests.post("http://localhost:11434/api/chat",
        json={"model": "llama3", "messages": full_messages}
    )
    # Split response by lines, parse JSON, and concatenate content
    content = ""
    for line in res.text.strip().split("\n"):
        if not line:
            continue
        try:
            data = json.loads(line)
            content += data.get("message", {}).get("content", "")
        except json.JSONDecodeError:
            continue

    return content


# Chat endpoint
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_msg = data["message"]
    chat_id = get_or_create_chat(data.get("chat_id"))
    # Save user message
    save_message(chat_id, "user", user_msg)
    history = load_history(chat_id)
    # Compute embedding of user query
    embedded_tensor = embedder.encode([user_msg])[0]
    # convert to list for psycopg2. It doesn't accept neither tensor nor numpy array
    user_embedding = list(embedded_tensor)
    user_embedding = [float(x) for x in user_embedding]
    retrieved = retrieve_top_k(user_embedding, k=3)
    llm_answer = ask_llm(history, retrieved)
    # Save assistant's message
    save_message(chat_id, "assistant", llm_answer)

    return jsonify({
        "chat_id": chat_id,
        "answer": llm_answer,
        "retrieved_chunks": retrieved 
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
