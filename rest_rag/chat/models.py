from django.db import models
from django.conf import settings

# Create your models here.

class Conversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    conversation =  models.ForeignKey(Conversation, on_delete= models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=10, choices = (("user", "User"), ("ai", "AI")))
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)