from django.urls import path
from .views import ChatView, ConversationDeleteView

app_name = "chat"

urlpatterns = [
    path("chat/", ChatView.as_view(), name="chat"),
    path(
        "conversation/<int:pk>/delete/",
        ConversationDeleteView.as_view(),
        name="delete_conversation",
    ),
]
