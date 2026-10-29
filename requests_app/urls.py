from django.urls import path
from . import views


app_name = "requests_app"


urlpatterns = [

    # =====================================
    # SERVICE REQUESTS
    # =====================================

    path(
        "",
        views.ServiceRequestListView.as_view(),
        name="list"
    ),

    path(
        "add/",
        views.ServiceRequestCreateView.as_view(),
        name="add"
    ),

    path(
        "<int:pk>/edit/",
        views.ServiceRequestUpdateView.as_view(),
        name="edit"
    ),

    path(
        "<int:pk>/delete/",
        views.ServiceRequestDeleteView.as_view(),
        name="delete"
    ),
]