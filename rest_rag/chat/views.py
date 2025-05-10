import os
from dotenv import load_dotenv

from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from .models import Conversation, Message
from django.urls import reverse, reverse_lazy
from documents.models import Documents
from django.contrib import messages
from rag.rag_utils import embed_query, get_chroma_client, get_chroma_vectorstore
from groq import Groq
from django.http import StreamingHttpResponse, JsonResponse
from django.views.generic import DeleteView
import json
import markdown

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)


# Create your views here.
class ChatView(LoginRequiredMixin, View):

    def get(self, request):
        conversation, _ = Conversation.objects.get_or_create(user=request.user)
        messages = conversation.messages.order_by("created_at")

        return render(
            request,
            "chat/chat.html",
            {
                "messages": messages,
                "username": request.user.username,
                "conversation": conversation,
            },
        )

    def post(self, request):
        content = request.POST.get("content")
        conversation, _ = Conversation.objects.get_or_create(user=request.user)

        if content:
            Message.objects.create(
                conversation=conversation, sender="user", content=content
            )

            vectorstore = get_chroma_vectorstore(request.user.id)
            embedding = embed_query(content)

            docs = vectorstore.similarity_search_by_vector(embedding, k=5)
            context_docs = [doc.page_content for doc in docs]

            context_text = "\n\n".join(context_docs)
            prompt = f""" 
            "You are an AI assistant. The user has uploaded a document and wants to have a conversation about its contents. Answer the user's questions using the information from the uploaded document.  \n\n Context: \n{context_text}\n\n User: {content}\n AI: """

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return StreamingHttpResponse(
                    streaming_content=streaming_groq_response(prompt, conversation),
                    content_type="text/event-stream",
                )

            response = call_groq(prompt)

            Message.objects.create(
                conversation=conversation,
                sender="ai",
                content=markdown.markdown(
                    response, extensions=["extra", "nl2br", "sane_lists"]
                ),
            )

        return redirect(reverse("chat:chat"))


class ConversationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Conversation
    success_url = reverse_lazy("chat:chat")

    def test_func(self):
        conversation = self.get_object()
        return conversation.user == self.request.user


def call_groq(prompt):
    stream = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        stream=True,
    )

    response_text = ""

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            response_text += delta.content

    return response_text


def streaming_groq_response(prompt, conversation):
    stream = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        stream=True,
    )

    full_response = ""

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            full_response += delta.content
            yield f"data: {json.dumps({'chunk': delta.content})}\n\n"

    Message.objects.create(
        conversation=conversation,
        sender="ai",
        content=full_response,
    )

    yield f"data: {json.dumps({'done': True})}\n\n"
