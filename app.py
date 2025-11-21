from flask import Flask, request, jsonify
from uuid import uuid4
import psycopg2
import requests
from sentence_transformers import SentenceTransformer

# Setup section
app = Flask(__name__)
# Database connection, we use PostgreSQL pgvector extension for vector storage of 
# our chunks of text
conn = psycopg2.connect(
    host="localhost",
    database="metropolia",
    user="postgres",
    password="pass"
)

embedder = SentenceTransformer("all-MiniLM-L6-v2")

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
        role = "user" if sender=="user" else "assistant"
        messages.append({"role": role, "content": content})
    return messages

def ask_llm(history):
    res = requests.post(
        "http://localhost:11434/api/chat",
        json={"model": "llama3", "messages": history}
    )
    return res.json()["message"]["content"]


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_msg = data["message"]
    chat_id = get_or_create_chat(data.get("chat_id"))

    save_message(chat_id, "user", user_msg)
    history = load_history(chat_id)
    user_embedding = embedder.encode([user_msg], convert_to_numpy=True)[0]  # numpy array

    llm_answer = ask_llm(history)

    save_message(chat_id, "assistant", llm_answer)

    return jsonify({
        "chat_id": chat_id,
        "answer": llm_answer
    })


if __name__ == '__main__':
    app.run(auto_reload = True, host='0.0.0.0', port=5000, debug=True)