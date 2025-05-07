from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .models import Documents
from rag.chroma_utils import (
    extract_text,
    chunk_text,
    get_chroma_client,
    get_chroma_vectorstore,
    add_texts_to_user_store,
)


class DocumentUploadView(View):
    def get(self, request):
        docs = Documents.objects.filter(user=request.user).order_by("-uploaded_at")

        return render(request, "documents/document.html", {"documents": docs})

    def post(self, request):
        uploaded_file = request.FILES.get("document")
        if uploaded_file:
            doc = Documents.objects.create(
                user=request.user, document_name=uploaded_file.name, file=uploaded_file
            )

            temp_path = f"/tmp/{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())

            try:
                full_text = extract_text(temp_path)
                chunks = chunk_text(full_text)
                metadata = [{"source": doc.title}] * len(chunks)
                add_texts_to_user_store(request.user.id, chunks, metadata)
                messages.success(request, f" '{doc.title}' upload and processed.")
            except Exception as e:
                messages.error(request, f"Error processing document: {e}")

            return redirect("documnets:upload") 

        docs = Documents.objects.filter(user=request.user).order_by("-uploaded_at")
        return render(request, "documents/document.html", {"documents": docs})
