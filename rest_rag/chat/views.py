from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .models import Conversation, Message
from django.urls import reverse

# Create your views here.
class ChatView(LoginRequiredMixin, View):

    def get(self, request):
        conversation, _ = Conversation.objects.get_or_create(user=request.user)
        messages = conversation.messages.order_by("created_at")

        return render(request, "chat/chat.html", {
            "messages": messages,
            "username": request.user.username
        })
    
    def post(self, request):
        content = request.POST.get("content")
        if content:
            conversation, _ = Conversation.objects.get_or_create(user = request.user)

            Message.objects.create(conversation = conversation, sender = "user", content = content)

            Message.objects.create(conversation = conversation, sender = "ai", content = "This is the AI response. ")

        return redirect(reverse("index"))