from django.db import models
from django.conf import settings

# Create your models here.

class Documents(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    file = models.FileField(upload_to="documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    document_name = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.document_name or self.file.name
