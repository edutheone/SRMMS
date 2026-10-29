
from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    path("", views.ChatbotView.as_view(), name="chat"),
    path(
        "message/",
        views.ChatbotMessageView.as_view(),
        name="message",
    ),
]
