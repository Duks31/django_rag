from django.urls import path
from .views import DocumentUploadView

app_name = "documents"

urlpatterns = [
    path('', DocumentUploadView.as_view(), name = "upload")
]