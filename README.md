# AI-for-Metropolia
Using Flask to create a solution using AI for Metropolia

# Overview

This project is an AI-powered navigation assistant for Metropolia University of Applied Sciences.
It helps students quickly find information across the university’s website (e.g., schedules, course registration, student services) using:

* Local LLM (via Ollama)

* Semantic search using embeddings (pgvector + PostgreSQL)

* Flask backend

* Persistent chat history

* RAG (Retrieval-Augmented Generation)

*(NOT YET)* Students can start conversations, return later, and continue where they left off.
The system retrieves relevant website content using embeddings and assists the user conversationally.
For current demo project will be used a text from [link](https://opiskelija.oma.metropolia.fi)

# Tech stack
## Python:
* Flask
* BeatifulSoup
* LangChain
## DB:
* PostgreSQL
* FAISS
## Embeddings
* Sentence-Transformers
## LLM Runtime
* Ollama

# Authors:

> Metropolia AI Project – Student Developer
> Grigorii 
