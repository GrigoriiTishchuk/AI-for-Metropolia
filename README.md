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
For current demo project will be used a text from [link](https://metropolia.fi) and a bit further

# Tech stack
## Python:
* Flask
* BeatifulSoup
* LangChain
## DB:
* PostgreSQL
* PG_Vector
## Embeddings
* Sentence-Transformers
## LLM Runtime
* Ollama

# Python Environment Setup
1. Install Python 3.12 (or compatible)

Download from python.org
Make sure Add Python to PATH is checked during installation.

Verify installation:
```
python --version
pip --version
```
2. Create a Virtual Environment (Recommended)

Open a terminal in your project folder:
```
python -m venv venv
```

Activate it:
```
venv\Scripts\activate
```

You should see (venv) in your prompt, meaning the virtual environment is active.

3. Install Required Python Libraries

Install libraries listed in requirements.txt (or manually):
```
pip install --upgrade pip

pip install flask
pip install psycopg2-binary
pip install requests
pip install beautifulsoup4
pip install readability-lxml
pip install sentence-transformers
pip install langchain-text-splitters
```

* Flask → web framework for your API
* psycopg2-binary → PostgreSQL database connection
* requests → HTTP requests for fetching pages
* beautifulsoup4 → HTML parsing
* readability-lxml → extract main content from web pages
* sentence-transformers → generate vector embeddings
* langchain-text-splitters → split web page text into chunks

If using requirements.txt, just run:
```
pip install -r requirements.txt
```
4. Verify Installations

Run Python and import all modules:
```
python
>>> import flask
>>> import psycopg2
>>> import requests
>>> import bs4
>>> import readability
>>> from sentence_transformers import SentenceTransformer
>>> from langchain_text_splitters import RecursiveCharacterTextSplitter
```

No errors → all libraries installed correctly.



# Installation DB guide:
pgvector Installation Guide (Windows 11)

This guide explains how to install the pgvector extension for PostgreSQL on Windows 11, which is required to store and query vector embeddings for AI applications.

1. Prerequisites

* PostgreSQL installed (tested with version 17).

* Visual Studio C++ Build Tools (or Visual Studio Community edition) with Desktop development with C++ workload.

* Git installed for cloning the pgvector repository.

2. Open the Correct Terminal

* Search for “x64 Native Tools Command Prompt for VS 2019” or later versions in the Start Menu.

* Open it as administrator.

This terminal has the necessary environment variables and paths for nmake.

3. Clone pgvector Repository

In the terminal, run:
```
cd C:\
git clone https://github.com/pgvector/pgvector.git
cd pgvector
```
4. Set PostgreSQL Root Directory

* Tell the build system where PostgreSQL is installed:
```
set "PGROOT=C:\Program Files\PostgreSQL\17"
```

Adjust the path according to your PostgreSQL installation directory.

You can verify that pg_config.exe exists:
```
dir "%PGROOT%\bin\pg_config.exe"
```
5. Build and Install pgvector

Run the following commands in the same terminal:
```
nmake /F Makefile.win
nmake /F Makefile.win install
```

nmake /F Makefile.win → compiles pgvector

nmake /F Makefile.win install → installs pgvector into PostgreSQL

6. Enable pgvector in Your Database

Open pgAdmin (or psql, or DataGrid by JetBrains) and connect to your database (e.g., metropolia).

Open the Query Tool.

Run:
```
CREATE EXTENSION vector;
```
This activates pgvector in your database. You only need to run this once per database.

Verify installation:
```
SELECT * FROM pg_available_extensions WHERE name='vector';
```

You should see vector listed with its version and description.

7. Test Vector Functionality
```
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    embedding VECTOR(3)
);

INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');
SELECT * FROM items;
```

This confirms that you can create tables with vector columns and insert vector data.

8. Troubleshooting

PGROOT not set error → Make sure you set PGROOT correctly in the VS developer terminal.

nmake not recognized → Use x64 Native Tools Command Prompt with C++ build tools installed.

Permissions → Run terminal as administrator.

# How to boot/run the app




# Authors:

> Metropolia AI Project – Student Developer
> Grigorii 
