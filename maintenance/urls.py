from django.urls import path
from . import views


app_name = "maintenance"


urlpatterns = [

    # =====================================
    # MAINTENANCE SCHEDULES
    # =====================================

    path(
        "",
        views.MaintenanceScheduleListView.as_view(),
        name="list"
    ),

    path(
        "add/",
        views.MaintenanceScheduleCreateView.as_view(),
        name="add"
    ),

    path(
        "<int:pk>/edit/",
        views.MaintenanceScheduleUpdateView.as_view(),
        name="edit"
    ),

    path(
        "<int:pk>/delete/",
        views.MaintenanceScheduleDeleteView.as_view(),
        name="delete"
    ),
]