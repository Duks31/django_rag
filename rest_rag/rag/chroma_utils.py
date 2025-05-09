import chromadb
import chromadb.config
import os
import fitz  # PyMuPDF
import docx
from django.conf import settings
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def extract_text(file_path: str) -> str:
    """
    Detect file type and extract plain text.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_from_pdf(file_path)
    elif ext == ".docx":
        return extract_from_docx(file_path)
    elif ext == ".txt":
        return extract_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def extract_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF using PyMuPDF.
    """
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def extract_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file using python-docx.
    """
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_from_txt(file_path: str) -> str:
    """
    Read plain text from a TXT file.
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )
    return splitter.split_text(text)


def get_chroma_client(user_id):
    persist_dir = Path(settings.BASE_DIR) / ".chroma" / f"user_{user_id}"
    persist_dir.mkdir(parents=True, exist_ok=True)
    print(f"Chroma client initialized at: {persist_dir}")

    return chromadb.Client(
        path=str(persist_dir),
        settings=chromadb.config.Settings(chroma_db_impl="duckdb+parquet"),
    )


def get_chroma_vectorstore(user_id):
    persist_dir = Path(settings.BASE_DIR) / ".chroma" / f"user_{user_id}"
    persist_dir.mkdir(parents=True, exist_ok=True)

    return Chroma(
        collection_name=f"user_{user_id}_collection",
        embedding_function=embedding_model,
        persist_directory=str(persist_dir),
    )


def add_texts_to_user_store(user_id, texts, metadata=None):
    store = get_chroma_vectorstore(user_id)
    store.add_texts(texts, metadatas=metadata or [{} for _ in texts])
