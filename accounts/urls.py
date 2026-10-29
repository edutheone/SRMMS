
from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),

    # User management
    path(
        "users/",
        views.UserListView.as_view(),
        name="user_list",
    ),
    path(
        "users/add/",
        views.UserCreateView.as_view(),
        name="user_add",
    ),
    path(
        "users/<int:pk>/edit/",
        views.UserUpdateView.as_view(),
        name="user_edit",
    ),
]
