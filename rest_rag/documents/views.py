from django.shortcuts import render, redirect
from django.views import View
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Documents
from rag.rag_utils import (
    extract_text,
    chunk_text,
    get_chroma_client,
    get_chroma_vectorstore,
    add_texts_to_user_store,
)

import os
import tempfile
from pathlib import Path


class DocumentUploadView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    def get(self, request):
        docs = Documents.objects.filter(user=request.user).order_by("-uploaded_at")

        return render(request, "documents/document.html", {"documents": docs})

    def post(self, request):
        uploaded_file = request.FILES.get("document")

        if not uploaded_file:
            messages.error(request, "No file uploaded")
            return redirect("document:upload")

        doc = Documents.objects.create(
            user=request.user, document_name=uploaded_file.name, file=uploaded_file
        )

        try:
            print("Starting")

            with tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(uploaded_file.name).suffix
            ) as tmp:
                for chunk in uploaded_file.chunks():
                    tmp.write(chunk)
                temp_path = tmp.name

            full_text = extract_text(temp_path)
            print("Text extracted")

            chunks = chunk_text(full_text)
            print("Text chunked")

            metadata = [{"source": doc.document_name}] * len(chunks)
            add_texts_to_user_store(request.user.id, chunks, metadata)
            print("Chunks added to vector store")

            messages.success(
                request, f"'{doc.document_name}' uploaded and processed successfully."
            )

        except Exception as e:
            messages.error(request, f"Error processing document: {e}")
            print(f"Exception: {e}")

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

            return redirect("documents:upload")


class DocumentDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        doc = get_object_or_404(Documents, pk=pk, user=request.user)

        if doc.file and os.path.exists(doc.file.path):
            os.remove(doc.file.path)

        try:
            store = get_chroma_vectorstore(request.user.id)
            store.delete(where={"source": doc.document_name})
            print(f"deleted vectors for: {doc.document_name}")
        except Exception as e:
            print(f"Error deleting vectors: {e}")

        doc.delete()
        messages.success(request, "Documents asnn associated vectors have been deleted")

        return redirect("documents:upload")
