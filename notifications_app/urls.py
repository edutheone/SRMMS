from django.urls import path
from . import views


app_name = "notifications_app"


urlpatterns = [

    # =====================================
    # NOTIFICATIONS
    # =====================================

    path(
        "",
        views.NotificationListView.as_view(),
        name="list"
    ),

    path(
        "<int:pk>/read/",
        views.NotificationMarkReadView.as_view(),
        name="mark_read"
    ),

    path(
        "mark-all-read/",
        views.NotificationMarkAllReadView.as_view(),
        name="mark_all_read"
    ),

    path(
    "popup/",
    views.NotificationPopupView.as_view(),
    name="popup"
),

]