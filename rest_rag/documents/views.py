from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .models import Documents

class DocumentUploadView(View):
    def get(self, request):
        docs = Documents.objects.filter(user=request.user).order_by('-uploaded_at')

        return render(request, 'documents/document.html', {
            'documents': docs
        })
    
    def post(self, request):
        uploaded_file = request.FILES.get('document')
        if uploaded_file:
            doc = Documents.objects.create(
                user=request.user,
                document_name=uploaded_file.name,
                file=uploaded_file
            )
            messages.success(request, f"“{doc.document_name}” uploaded successfully.")
            return redirect('documents:upload')
        
        docs = Documents.objects.filter(user=request.user).order_by('-uploaded_at')
        return render(request, 'documents/document.html', {'documents': docs})
    
