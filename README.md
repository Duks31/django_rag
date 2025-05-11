# 🧠 rest_rag – RAG-Based Chat with Django REST Framework

**rest_rag** is a lightweight Retrieval-Augmented Generation (RAG) chat application built with Django REST Framework. Users can upload documents and chat with an AI assistant that understands and responds based on the uploaded content.

---

## Features

- 🔐 User authentication (Login/Register)
- 📄 Document upload with parsing
- 💬 Chat interface with context-aware responses
- 🧠 RAG pipeline for document-based Q&A
- ⚙️ Django REST API backend
- 🎨 Simple HTML(Django template) frontend

---

## Tech Stack

- **Backend:** Django, Django REST Framework
- **AI/NLP:** Groq(OpenAI API) and ChromaDB
- **Database:** PostgreSQL

---

## Installation

```bash
git clone https://github.com/Duks31/django_rag
cd rest_rag

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run the server
python manage.py runserver
```
