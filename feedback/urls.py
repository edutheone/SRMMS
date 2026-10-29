from django.urls import path
from . import views


app_name = "feedback"


urlpatterns = [

    # =====================================
    # FEEDBACK
    # =====================================

    path(
        "",
        views.FeedbackListView.as_view(),
        name="list"
    ),

    path(
        "add/",
        views.FeedbackCreateView.as_view(),
        name="add"
    ),

    path(
        "<int:pk>/edit/",
        views.FeedbackUpdateView.as_view(),
        name="edit"
    ),

    path(
        "<int:pk>/delete/",
        views.FeedbackDeleteView.as_view(),
        name="delete"
    ),
]