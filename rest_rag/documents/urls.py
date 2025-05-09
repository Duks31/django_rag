from django.urls import path
from .views import DocumentUploadView, DocumentDeleteView

app_name = "documents"

urlpatterns = [
    path('', DocumentUploadView.as_view(), name = "upload"),
    path("delete/<int:pk>/", DocumentDeleteView.as_view(), name = "delete"),
]   