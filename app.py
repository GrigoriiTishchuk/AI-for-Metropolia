from flask import Flask, request, jsonify
from uuid import uuid4
import psycopg2
import requests
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv
import os

# Setup section
app = Flask(__name__)

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
    
    new_chat = str(uuid4())
    cur.execute("INSERT INTO chats (chat_id) VALUES (%s);", (new_chat,))
    conn.commit()
    return new_chat


def save_message(chat_id, sender, content):
    cur = conn.cursor()
    mid = str(uuid4())
    cur.execute("""
        INSERT INTO messages (message_id, chat_id, sender, content)
        VALUES (%s, %s, %s, %s);
    """, (mid, chat_id, sender, content))
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
def retrieve_top_k(user_embedding, k=3):
    cur = conn.cursor()

    # pgvector requires Python list, not numpy
    emb_list = user_embedding.tolist()

    cur.execute("""
        SELECT text
        FROM chunks
        ORDER BY embedding <-> %s
        LIMIT %s;
    """, (emb_list, k))

    rows = cur.fetchall()
    return [row[0] for row in rows]

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

    # Insert system message at the start
    full_messages = [{"role": "system", "content": system_prompt}] + history
    res = requests.post(
        "http://localhost:11434/api/chat",
        json={"model": "llama3", "messages": full_messages}
    )
    return res.json()["message"]["content"]


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
    user_embedding = embedder.encode([user_msg], convert_to_numpy=True)[0]
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
    app.run(auto_reload=True, host='0.0.0.0', port=5000, debug=True)
